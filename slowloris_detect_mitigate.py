# slowloris_detect_mitigate.py
#Bakr alkhalidi

import subprocess
import time
import re
import sqlite3
from collections import Counter

# Configuration
PORT = "80"
CONNECTION_THRESHOLD = 10
INCOMPLETE_RATIO_THRESHOLD = 0.5
CHECK_INTERVAL = 5
BLOCK_DURATION = 120
PACKET_CAPTURE_COUNT = 400

blocked_ips = set()
block_times = {}

class DatabaseLogger:
    def __init__(self, db_file='db_data/monitoring.db'):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS connection_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip TEXT,
                status TEXT,
                reason TEXT
            )
        ''')
        self.conn.commit()

    def log_event(self, ip, status, reason=None):
        self.cursor.execute('INSERT INTO connection_logs (ip, status, reason) VALUES (?, ?, ?)', (ip, status, reason))
        self.conn.commit()

    def close(self):
        self.conn.close()
# scan active connections using netstat
def get_connection_counts():
    result = subprocess.run(["netstat", "-an"], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    connections = []
		
    for line in lines:
        if f":{PORT}" in line and "ESTABLISHED" in line:
            try:
                parts = line.split()
                ip_port = parts[4]
                ip = ip_port.split(":")[0]
                if ip != "127.0.0.1":
                    connections.append(ip)
            except IndexError:
                continue
    return Counter(connections)
#use tcpdump to capture HTTP traddic from given IP
def analyze_http_traffic(ip):
    try:
        result = subprocess.run(
            ["sudo", "tcpdump", "-A", "-nn", "-i", "any", f"host {ip} and tcp port {PORT}", "-c", str(PACKET_CAPTURE_COUNT), "-s", "2048"],
            capture_output=True, text=True, timeout=30
        )
        packets = result.stdout
        print(f"[DEBUG] Captured payload from {ip} (length={len(packets)}):\n{packets[:500]}")

        all_requests = re.findall(r"(GET|POST|PUT|DELETE|HEAD) .*?HTTP/\d\.\d", packets)
        complete_requests = re.findall(r"HTTP/\d\.\d.*?\r\n\r\n", packets, re.DOTALL)

	#checks how many requests are complete vs incomplete

        total = len(all_requests)
        complete = len(complete_requests)
        incomplete = total - complete

        if total >= 1:
            ratio = incomplete / total
            print(f"[+] {ip} - {incomplete}/{total} incomplete HTTP requests ({ratio:.1%})")
            return ratio > INCOMPLETE_RATIO_THRESHOLD
        elif "User-Agent" not in packets and "Host:" not in packets:
            print(f"[!] {ip} - Suspicious traffic: HTTP header fields missing, marking as Slowloris")
            return True
        else:
            print(f"[i] {ip} - Not enough HTTP traffic captured for decision")
            return False
    except subprocess.TimeoutExpired:
        print(f"[!] Timeout while inspecting IP: {ip}")
    except Exception as e:
        print(f"[!] Error sniffing {ip}: {e}")
    return False
#apply a iptables rule to drop packets from attack
def block_ip(ip):
    print(f"[!] Blocking malicious IP: {ip}")
    subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-p", "tcp", "--dport", PORT, "-j", "DROP"])
    blocked_ips.add(ip)
    block_times[ip] = time.time()

#unblocks the IP
def unblock_expired_ips(db_logger):
    now = time.time()
    for ip in list(blocked_ips):
        if now - block_times[ip] > BLOCK_DURATION:
            print(f"[+] Unblocking IP: {ip}")
            subprocess.run(["sudo", "iptables", "-D", "INPUT", "-s", ip, "-p", "tcp", "--dport", PORT, "-j", "DROP"])
            blocked_ips.remove(ip)
            del block_times[ip]
            db_logger.log_event(ip, "unblocked", "Timeout expired")
#main detection loop
def main():
    print("[+] Slowloris Defense is running..")
    db_logger = DatabaseLogger() #blocks and log it

    try:
        while True:
            connection_counts = get_connection_counts()
            for ip, count in connection_counts.items():
                print(f"[*] {ip} has {count} connections")
                if ip in blocked_ips:
                    continue
                if count >= CONNECTION_THRESHOLD:
                    if analyze_http_traffic(ip):
                        block_ip(ip)
                        db_logger.log_event(ip, "blocked", "Slowloris detected (Incomplete HTTP headers)")
            unblock_expired_ips(db_logger)
            time.sleep(CHECK_INTERVAL)
    finally:
        db_logger.close()

if __name__ == "__main__":
    main()


