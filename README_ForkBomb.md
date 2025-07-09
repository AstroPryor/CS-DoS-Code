Cloud Security Project - Fork Bomb Detection and Mitigation

The following files are all mine
fork_bomb.sh
monitoring.py
detector.py
Dockerfile

This project focused on making a security monitoring and detection system that focuses on identifying and mitigating process based attacks. mainly fork bombs within a container.

Overview

This project has 3 major components

A monitoring system utilizing SQLite database to log process counts
A detection system to analyze data for potential fork bombs
A simulated attack to test the system

Components
Monitoring System (monitoring.py)

Collects process count data every second
Stores data in SQLite database for analysis
Provides real-time visibility into system resource usage

Detection System (detector.py)

Analyzes process counts and growth rates
Triggers mitigation when predefined thresholds are exceeded:

Process count > 800
Process growth rate > 25 processes per second


Executes mitigation strategies when attacks are detected

Attack Simulation (fork_bomb.sh)

Simulates a common bash fork bomb for testing.

Setup and Usage requirements:

Python 3.10+

Building and Running

Build the Docker image:

bashdocker build -t cloud_security_project .

Run the container:

bashdocker run --name cloud_security_project_container cloud_security_project

Overview of how it works:

The monitoring system logs the process counts to a SQLite database every second. 
The detector reads and analyzes this data looking for an unusual process growth
When an attack is detected the system executes the mitigation
The fork bomb script is used to simulate the attack.

Detection logic:

Uses two ways to detect a fork bomb both have to be met to mitigate:
1. Absolute threshold: this is a process threshold that has to be met before mitigation (set to 800 in testing)
2. Rate threshold: this is a rate threshold that calculates how fast the processes are growing.

Mitigation Strategy
When a fork bomb is detected, the system:

Logs the detection event
Attempts to kill all user processes
Records the mitigation action

Dockerfile

FROM python:3.10-slim

# Install necessary packages, including psmisc (for killall)
RUN apt-get update && apt-get install -y psmisc

# Set the working directory
WORKDIR /app

# Copy all files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir psutil

# Make your scripts executable
RUN chmod +x fork_bomb.sh

# Run all scripts concurrently (monitoring, detector, fork_bomb)
CMD ["sh", "-c", "python3 monitoring.py & python3 detector.py & ./fork_bomb.sh & wait"]

Warning
This project is intended for educational purposes and security testing in isolated environments. The included fork bomb script can cause system instability and should never be executed on production systems.
Project Structure

KNOWN ISSUES:
within the container when running all 3 codes at once the detection and monitoring code do not output but still run. you can check this by taking out the fork_bomb.sh and it will show the monitoring





