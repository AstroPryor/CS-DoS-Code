#!/usr/bin/env python3
# import the libraries
import socketserver
import threading
import time
import argparse
from collections import defaultdict, deque
import subprocess
import os
import sqlite3
# main protection class that implements SYN flood detection and blockin
class SynFloodProtection:
    def __init__(self, max_half_open=50, detection_window=5, rate_limit=20):
        self.half_open_connections = defaultdict(int)
        self.connection_history = defaultdict(lambda: deque(maxlen=100))
        self.blacklist = set()
        self.max_half_open = max_half_open
        self.detection_window = detection_window
        self.rate_limit = rate_limit
        self.lock = threading.Lock()
        self.init_db()
#initializes the SQLite database for logging
    def init_db(self):
        self.conn = sqlite3.connect('monitoring.db')
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
# logs the events to the database
    def log_event(self, ip, status, reason=None):
        self.cursor.execute('INSERT INTO connection_logs (ip, status, reason) VALUES (?, ?, ?)', 
                            (ip, status, reason))
        self.conn.commit()
# checks if the client IP should be allowed or blocked
    def check_connection(self, client_address):
        ip = client_address[0]
        current_time = time.time()

        with self.lock:
            if ip in self.blacklist:
                self.log_event(ip, 'blocked', 'already_blacklisted')
                return False

            self.connection_history[ip].append(current_time)
            connections_in_window = len([t for t in self.connection_history[ip] if current_time - t <= self.detection_window])
# if the connection rate exceeds the threshold then it blacklists the IP
            if connections_in_window > self.rate_limit or self.half_open_connections[ip] > self.max_half_open:
                if ip not in self.blacklist:
                    self.blacklist.add(ip)
                    print(f"IP BLOCKED: {ip}")
                    self.block_ip(ip)
                    reason = 'rate_limit' if connections_in_window > self.rate_limit else 'half_open'
                    self.log_event(ip, 'blocked', reason)
                return False
# otherwise it allows the connection
            self.half_open_connections[ip] += 1
            self.log_event(ip, 'allowed')
        return True
# adds the iptables rule to blovk traffic from IP
    def block_ip(self, ip):
        try:
            subprocess.run(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"], check=True)
            print(f"Iptables rule added to block {ip}")
        except subprocess.CalledProcessError:
            print(f"Failed to block IP {ip} via iptables")
# is called when a connection is established successfully
    def connection_established(self, client_address):
        ip = client_address[0]
        with self.lock:
            self.half_open_connections[ip] = max(0, self.half_open_connections[ip] - 1)
#called when the connection closes
    def connection_closed(self, client_address):
        ip = client_address[0]
        with self.lock:
            self.half_open_connections[ip] = max(0, self.half_open_connections[ip] - 1)
#TCP server that uses the protection mechanism
class ProtectedTCPServer(socketserver.ThreadingTCPServer):
    def __init__(self, server_address, RequestHandlerClass, protection):
        self.protection = protection
        super().__init__(server_address, RequestHandlerClass)
        self.allow_reuse_address = True

    def verify_request(self, request, client_address):
        return self.protection.check_connection(client_address)
# handles the individual client connections
class ProtectedRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.server.protection.connection_established(self.client_address)
        try:
            data = self.request.recv(1024)
            while data:
                self.request.sendall(data)
                data = self.request.recv(1024)
        except:
            pass
        finally:
            self.server.protection.connection_closed(self.client_address)
# entry point to start the protected server
def run_server(host, port, max_half_open, detection_window, rate_limit):
    protection = SynFloodProtection(max_half_open, detection_window, rate_limit)
    server = ProtectedTCPServer((host, port), ProtectedRequestHandler, protection)
    print(f"Server running on {host}:{port} | PID: {os.getpid()}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server.shutdown()
        server.server_close()
# parses through CLI arguments and starts the server
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SYN Flood Protection Server with DB Logging")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--max-half-open", type=int, default=50)
    parser.add_argument("--window", type=int, default=5)
    parser.add_argument("--rate-limit", type=int, default=20)

    args = parser.parse_args()

    if os.geteuid() != 0:
        print("This script must be run as root to modify iptables.")
        exit(1)

    run_server(args.host, args.port, args.max_half_open, args.window, args.rate_limit)
