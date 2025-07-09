README

**for educational purposes only. Should only be used inside a virtual VM.
**Need sudo access to run these.

By: Bakr Alkhalidi
CSCE 3560

-------------------------

Description of the program

- The Slowloris attack sends multiple incomplete HTTP headers to a server, consuming sockets and causing service disruption.
- The `slowloris_detect_mitigate.py` script detects this behavior using TCP connection monitoring and HTTP header analysis.
- Once an attack is identified, the IP is blocked using `iptables`.
- The system logs all events into an SQLite database.

--------------------------
notes: make sure you run it on sudo for the root privilege.
run: ulimit -n 4096
-this is to increase the open file limit

1-To run the program first install docker and build tools

sudo apt update
sudo apt install -y docker.io g++ make net-tools iputils-ping sqlite3


2-Then enable and start docker

sudo systemctl enable docker
sudo systemctl start docker

3-Then build the docker image

docker build -t slowloris-defender .

4-Run the defense system from docker

docker run -it   --cap-add=NET_ADMIN   --cap-add=NET_RAW   --network host   -v $(pwd)/db_data:/app/db_data   --name slowloris_defender   slowloris-defender


4-Compile the slowloris attack

g++ -std=c++0x -pthread slowloris_attack.cpp -o slowlorisattack

5-Run the attack
ex:
./slowlorisattack 127.0.0.1 80 200 5


./slowlorisattack <Target IP>  <Target port>  <number of sockets to open>  <num of threads to use>


-remove existing docker container if needed:

docker rm slowloris_defender


6-To check blocked IP run:

sudo iptables -L INPUT -n --line-numbers

7-To unblock IP manually:

sudo iptables -D <rule_number>

-ex:
sudo iptables -D Input 1


8-to check db

sqlite3 db_data/monitoring.db

-inside SQLite prompt:
To show all tables:

.tables

-To check the contents inside table:
SELECT * FROM connection_logs;

-To exit sqlite
.exit

-Notes:

ensure a web server is running on the VM (Apache)
This project simulates a network based container attack

