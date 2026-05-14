import psutil
from sklearn.ensemble import IsolationForest
import time
import sqlite3
from datetime import datetime

cpu_data = [] # CPU usage logs
my_pid = psutil.Process().pid # Store this program's process id

def init_db():
	conn = sqlite3.connect("cpu_data.db") # Connects to or creates the database fileif does not exist
	cursor = conn.cursor() # Cursor creation; allows for SQL command exeuction
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS process_usage (
			timestamp TEXT,
			pid INTEGER,
			name TEXT,
			cpu_percent REAL
		)
	''')
	conn.commit() # Save changes to database
	conn.close() # Close database connection

def log_to_db(process_list):
	conn = sqlite3.connect("cpu_data.db") # Connects to database
	cursor = conn.cursor()
	timestamp = datetime.now().isoformat()
	for i in process_list: # Inserts each processes' data
		cursor.execute('''
			INSERT INTO process_usage (timestamp, pid, name, cpu_percent)
			VALUES (?, ?, ?, ?)
		''', (timestamp, i['pid'], i['name'], i['cpu_percent']))
	conn.commit()
	conn.close()

def monitor_cpu():
	process_info = []
	seen_pids = set()
	for i in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent']): # Iterates over all running processes; retrieves process ID, name, and CPU percentage usage
		try: # If a process is not idle, the process is added to the process_info list
			cpu_percent = i.info['cpu_percent']
			pid = i.info['pid']
			if pid == my_pid: # Do not add this process to list; could be unintentionally killed
				continue
			if cpu_percent > 0 and pid not in seen_pids: # Ignores idle processes and previously seen processes
				seen_pids.add(pid)
				process_info.append({"pid": pid, "name": i.info['name'], "cpu_percent": cpu_percent})
		except (psutil.NoSuchProcess, psutil.AccessDenied):
			continue
	return process_info

def detect_anomaly(data):
	if len(data) > 10: # Start detection once enough data is collected for comparison
		cpu_values = [[entry["cpu_percent"]] for entry in data] # Converts dictionary to list of lists of CPU percentages; correct format for IsolationForest use
		model = IsolationForest(contamination=0.1, random_state=42) # IsolationForest model is created where 10% of data points are expected to be anomalies
		model.fit(cpu_values) # Builds the trees using CPU data, from which it establishes what is considered "normal" and is now ready to detect anomalies

		predictions = model.predict(cpu_values) # Classifies which CPU values are abnormal, where anomalies are listed as -1 in the list
		anomalies = []
		for i in range(len(predictions)): # Iterates through prediction list, and for each -1 in the list, the corresponding, malicious process is retrieved
			if predictions[i] == -1:
				anomalies.append(data[i]) # Add anomalous process to anomaly list
		return anomalies
	return []

def terminate_process(pid): # Terminates a process by PID
    try:
        process = psutil.Process(pid) # Retrieves process for the given PID
        process.terminate() # Kills the process
        print(f"Terminated high CPU usage process: {pid}")
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        print(f"Failed to terminate process: {pid}")
        return False

if __name__ == "__main__":
	init_db()
	failed_terminations = set() # Store process IDs of failed terminations
	try:
		while True:
			print(f"Monitoring...")
			usage = monitor_cpu() # Calls monitor_cpu() to retrieve usage of processes

			existing_pids = {entry['pid'] for entry in cpu_data} # Records all seen processes
			unique_usage = [entry for entry in usage if entry['pid'] not in existing_pids] # Ensures no duplication of process in the list and that the process is alive
			cpu_data.extend(unique_usage) # Adds data to cpu_data

			cpu_data = cpu_data[-30:] # Set limit on data to avoid memory overflow and for faster anomaly detection

			log_to_db(unique_usage) # Update database

			cpu_data = [entry for entry in cpu_data if psutil.pid_exists(entry['pid'])] # Ensures only alive proecses are in data to be analyzed

			anomalies = detect_anomaly(cpu_data) # Checks for anomalies in CPU usage
			if anomalies: # If there are anomalies, terminate them
				new_anomalies = [i for i in anomalies if i['pid'] not in failed_terminations] # Adds only new anomalies to the list

				if new_anomalies:
					print(f"Detected anomalous processes:\n{new_anomalies}")

				for i in new_anomalies: # Tries to terminate new anomalies
					pid = i['pid']
					if not terminate_process(pid): # If a process is not terminated, add the process to the list
						failed_terminations.add(pid)
			time.sleep(10) # Monitors every ten seconds
	except Exception as e: # Error handling
		print(f"An error occured: {e}")
