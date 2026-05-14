# Cloud DoS Detection and Mitigation Lab

## Overview

This project was developed for my Cloud Security course at the University of North Texas. It demonstrates a controlled lab environment for studying denial-of-service behavior and testing defensive mitigation techniques.

The project includes four simulated denial-of-service scenarios:

- SYN Flood
- CPU Exhaustion
- Slowloris, containerized with Docker
- Fork Bomb, containerized with Docker

Each attack has a corresponding mitigation script or defensive response. The goal of this project was not just to run attacks, but to understand the indicators of denial-of-service activity, observe system behavior during an attack, and apply practical mitigation techniques in a safe virtualized and containerized lab environment.

## Purpose

The purpose of this project was to:

- Simulate common denial-of-service attack patterns in a controlled environment
- Monitor host and network behavior during each attack
- Identify signs of resource exhaustion or abnormal traffic
- Apply mitigation techniques such as firewall rules, process control, and service hardening
- Document how defensive controls reduce or stop the attack impact
- Use Docker containers to isolate selected attack scenarios and make testing more repeatable

## Lab Environment

This project was tested in a local virtualized and containerized lab environment. The attack and defense scripts were intended for educational use only and were executed against systems owned and controlled by the project team.

Example environment:

- Linux virtual machines
- Docker containers for the Slowloris and Fork Bomb scenarios
- Python/Bash scripts
- Scapy for packet-based testing
- iptables/firewall rules for mitigation
- System monitoring tools for CPU, network, and process activity

## Containerized Lab Components

This project includes Docker-based lab components for the Slowloris and Fork Bomb scenarios. The Dockerfiles were used to isolate the test environment and make the attack and mitigation demonstrations easier to reproduce in a controlled setting.

Containerization helped with:

- Keeping the test environment separate from the host system
- Making the lab setup more repeatable
- Reducing the risk of accidentally affecting the main machine
- Testing mitigation behavior in a more controlled environment
- Documenting the environment needed to reproduce the scenario

The Dockerfiles are included only for controlled educational testing and should not be used against unauthorized systems.

## Attack and Mitigation Scenarios

### 1. SYN Flood

The SYN flood scenario simulates a high volume of TCP SYN packets sent to a target system. The mitigation focuses on identifying abnormal connection attempts and applying firewall-based controls to limit or block the traffic.

Key concepts demonstrated:

- TCP connection behavior
- SYN packet flooding
- Network traffic monitoring
- Firewall-based mitigation
- Controlled virtual machine testing

### 2. CPU Exhaustion

The CPU exhaustion scenario simulates excessive CPU usage to degrade system performance. The mitigation focuses on detecting abnormal process behavior and stopping or limiting the offending process.

Key concepts demonstrated:

- Resource exhaustion
- Process monitoring
- CPU utilization analysis
- Defensive process control
- Host-based mitigation

### 3. Slowloris

The Slowloris scenario simulates many slow, incomplete HTTP connections to exhaust server resources. This scenario includes a Dockerfile to help create a controlled and repeatable test environment.

The mitigation focuses on connection timeout controls, request limits, and service-level hardening.

Key concepts demonstrated:

- Application-layer denial-of-service behavior
- HTTP connection exhaustion
- Containerized testing
- Service hardening
- Timeout and connection limit mitigation

### 4. Fork Bomb

The fork bomb scenario demonstrates rapid process creation that can exhaust system resources. This scenario includes a Dockerfile to isolate the test environment and reduce the risk of affecting the host system.

The mitigation focuses on process limits and stopping runaway process behavior.

Key concepts demonstrated:

- Process exhaustion
- Linux process limits
- Containerized lab isolation
- Host protection strategies
- Resource control and mitigation

## Documentation

This repository includes individual README files for specific attack and mitigation scenarios. These files provide more detailed explanations of the scripts, expected behavior, and mitigation steps for each part of the project.

The main README provides the overall project summary, while the individual README files explain the separate attack and defense components.

## Safety and Ethics Notice

This project is for educational and defensive security research only. All testing should be performed only in a controlled lab environment on systems that you own or have explicit permission to test.

Do not run these scripts against public systems, third-party networks, production environments, or any system without authorization.

The attack scripts and Docker files are included to demonstrate denial-of-service behavior in a safe academic lab setting. They should not be used for malicious activity.

## What I Learned

Through this project, I gained hands-on experience with:

Denial-of-service attack behavior
Network and host-based indicators of compromise
Linux system monitoring
Firewall-based mitigation
Resource exhaustion risks
Defensive scripting
Docker-based lab isolation
Safe cybersecurity lab design
The importance of testing security controls in controlled environments

## Disclaimer

This repository is intended strictly for educational purposes, defensive security research, and controlled lab testing. The author does not condone unauthorized testing, disruption of services, or malicious use of the included materials.
  
## Repository Structure

```text
CS-DoS-Code/
├── Attack/
│   └── Attack scripts for each denial-of-service scenario
├── Docker/
│   └── Docker files for the Slowloris and Fork Bomb scenarios
├── Individual README's/
│   └── Scenario-specific README files and documentation
├── Mitigation/
│   └── Mitigation scripts and defensive responses
├── projectGroup7_codes.zip
│   └── Original packaged project files
└── README.md
