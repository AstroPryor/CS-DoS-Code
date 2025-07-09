README

**Both of these scripts are for educational purposes. They are meant to be run on personal virtual machines. 
** Please note that you need root or sudo access to run these scripts

-------------------------

Description of program
The mitigation script monitors incoming SYN packets and detects if they are not completing the handshake in real time
When an attack is detected, it will automatically block the malicious IP using iptables. 
From there, it will log all events into a SQLite database. 
The attack script generate SYN packets and send them to the desired IP address to simulate a SYN flood

-------------------------

To run both the syn flood and mitigation scripts, you need to install sqlite3 first
	sudo apt install sqlite3 (for the database)
From there, download both of the scripts into whatever directory you want.
Both of these scripts have to run in separate VMs

In the VM, you need to be in host only adapter and run these is  two separate VMs. 

**PLEASE NOTE THAT THIS DOES NOT WORK ON UNT WIFI (The IP address automatically changes to 10.0.2.15 and that doesn't allow the attack to get to the destination properly)
Run the mitigation first:
	sudo python3 syn_mitigation.py 
(There are optional arguments)

Then run the attack
	sudo python3 syn_attack.py <IP address> <port number> <duration> 
The mitigation should automatically block the IP that is sending the incomplete syn requests if there are more than 50 in 5 seconds or 20 SYN requests in the time frame.
** Please note the ip address should be the enp0s3 one
-------------------------

Features
- Real time SYN packet flood detection
- Auto blocks IP via iptables
- Logs all connections (allowed and blocked) to monitoring.db
- Customizable thresholds

-------------------------

Parameters
For the mitigation script, there are optional parameters that you can add
-- host 
Default: 0.0.0.0
-- port 
Default: 8080
-- max-half-open
Default: 50
-- window
Default: 5 seconds
-- rate-limit
Default: 20 connections per window
They all have defaults built into the code
Example:
sudo python3 syn_mitigation.py --port 9090 --rate-limit 10 --window 3

-------------------------

Database Information
Database Name: monitoring.db
Table Name: connection_logs

Columns:
- id
- timestamp
- ip
- status 
('allowed' or 'blocked')
- reason ('rate-limit' , 'half-open', 'already_blacklisted')

Example queries:

View the last 5 blocked IPs

	SELECT * FROM connection_logs
	WHERE status = 'blocked'
	ORDER BY timestamp DESC
	LIMIT 5;
	
For total connections
	SELECT COUNT(*) FROM connection_logs;
	
-------------------------
To see the IP blocked in iptables
	sudo iptables -L -n
To reset IP tables after testing run 
	sudo iptables -F 
	
-------------------------
End of File