# Cloud DoS Detection and Mitigation Lab

## Overview

This project was developed for my Cloud Security course at the University of North Texas. It demonstrates a controlled lab environment for studying denial-of-service behavior and testing defensive mitigation techniques.

The project includes four simulated denial-of-service scenarios:

- SYN Flood
- CPU Exhaustion
- Slowloris
- Fork Bomb

Each attack has a corresponding mitigation script or defensive response. The goal of this project was not just to run attacks, but to understand the indicators of denial-of-service activity, observe system behavior during an attack, and apply practical mitigation techniques in a safe virtual lab environment.

## Purpose

The purpose of this project was to:

- Simulate common denial-of-service attack patterns in a controlled environment
- Monitor host and network behavior during each attack
- Identify signs of resource exhaustion or abnormal traffic
- Apply mitigation techniques such as firewall rules, process control, and service hardening
- Document how defensive controls reduce or stop the attack impact

## Lab Environment

This project was tested in a local virtualized lab environment. The attack and defense scripts were intended for educational use only and were executed against systems owned and controlled by the project team.

Example environment:

- Linux virtual machines
- Python/Bash scripts
- Scapy for packet-based testing
- iptables/firewall rules for mitigation
- System monitoring tools for CPU, network, and process activity

## Attack and Mitigation Scenarios

### 1. SYN Flood

The SYN flood scenario simulates a high volume of TCP SYN packets sent to a target system. The mitigation focuses on identifying abnormal connection attempts and applying firewall-based controls to limit or block the traffic.

### 2. CPU Exhaustion

The CPU exhaustion scenario simulates excessive CPU usage to degrade system performance. The mitigation focuses on detecting abnormal process behavior and stopping or limiting the offending process.

### 3. Slowloris

The Slowloris scenario simulates many slow, incomplete HTTP connections to exhaust server resources. The mitigation focuses on connection timeout controls, request limits, and service-level hardening.

### 4. Fork Bomb

The fork bomb scenario demonstrates rapid process creation that can exhaust system resources. The mitigation focuses on process limits and stopping runaway process behavior.

## Repository Structure

```text
CS-DoS-Code/
├── attacks/
│   ├── syn_flood/
│   ├── cpu_exhaustion/
│   ├── slowloris/
│   └── fork_bomb/
├── mitigations/
│   ├── syn_flood_mitigation/
│   ├── cpu_exhaustion_mitigation/
│   ├── slowloris_mitigation/
│   └── fork_bomb_mitigation/
├── docs/
├── screenshots/
└── README.md
