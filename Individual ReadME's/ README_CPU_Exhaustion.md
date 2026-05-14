CPU Exhaustion README
README

All scripts provided are meant for personal, educational use only. Do not use these scripts to inflict harm upon others’ systems or networks.

-------------------------

Description of programs
The attack script, “CPU_Exhaustion.py”, creates multiple processes for each CPU core detected. In each of these processes, an infinite loop is run in order to keep the CPU busy. Then, it waits for each process to finish, which will never happen due to the infinite loop on each core.
The mitigation script, “CPU_Exhaustion_Response.py”, monitors all processes, looks out for anomalous CPU usage in processes, and automatically terminates these malicious processes via process id. All data collected from this program is logged in a SQL database for analysis.

-------------------------

Running the programs
In order to run these programs, you must have the correct libraries downloaded. You may need sudo access in order to override limitations. The libraries you will have to download are psutil, scikit-learn, and sqlite3. Here are the following installation commands, respectively:
	sudo apt install python3-psutil
	sudo apt-get install python3-sklearn python3-sklearn-lib python-sklearn-doc
	sudo apt install sqlite3
Now that you have the correct libraries, download the scripts.
Open two terminals, one for each script, and cd into the correct directory where each script is.
First, run the mitigation script with:
	python3 CPU_Exhaustion_Response.py
Then, run the attack script with:
	python3 CPU_Exhaustion.py
The mitigation script will then monitor all processes that are alive and running. All processes are recorded. To clean up output, duplicates of the same processes will not be recorded. The unique data is then collected. This unique data is sent to the SQL database. Once enough data is collected, processes are analyzed by an IsolationForest model which predicts which CPU usage values are abnormal. These processes are marked with a -1 in the list. and the process is inserted into the anomaly list. If there are anomalies in the anomaly list, each anomaly is attempted to be terminated. Repeated termination attempts will not be attempted to clean up output. This infinite loop happens every ten seconds. Once satisfied, terminate the mitigation script with Ctrl+C.
The attack script should be terminated within ten seconds to thirty seconds on average.

-------------------------

Features
-Live CPU monitoring, anomaly detection, and termination of malicious processes
-Error handling
-SQL database logging

-------------------------

Database Information
Database name: cpu_data.db
Tables: process_usage
	process_usage columns:
		Date and time
		Process ID
		Process Name
		CPU usage percentage
Possible queries:
	SELECT * FROM process_usage;
		Displays all logged processes
	SELECT * FROM process_usage LIMIT 5;
		Displays the 5 first processes logged
	SELECT * FROM process_usage ORDER BY timestamp DESC LIMIT 5;
		Displays the 5 most recent processes logged in descending order (earliest to latest)

-------------------------

Known Errors
The IsolationForest model may wrongly predict anomalies and kill low usage processes.
The mitigation script may accidentally close the terminal in which both scripts are running.
Mitigation may not work on certain VM setups.

-------------------------

END OF FILE
