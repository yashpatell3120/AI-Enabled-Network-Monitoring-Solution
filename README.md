# AI-enabled Network Monitoring Solution

## Project Description
The AI-enabled Network Monitoring Solution provides unified visibility into network health by combining traditional telemetry collection with AI-driven analytics. It continuously gathers device metrics, analyzes traffic behavior, and highlights anomalies so that operators can resolve issues faster and maintain reliable connectivity across distributed infrastructure.

## Setup Instructions
1. Clone the repository and enter the project directory:
   ```bash
   git clone https://github.com/example/ai-enabled-network-monitoring-solution.git
   cd ai-enabled-network-monitoring-solution
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure credentials, SNMP community strings, and alert destinations in `config.yaml` before running the services.

## Architecture
The solution is composed of modular services that communicate over message queues to ensure scalability and reliability:
- **Collectors** gather SNMP and ICMP telemetry from routers, switches, and servers at configurable intervals.
- **Data Pipeline** normalizes incoming metrics, enriches them with topology context, and stores historical records in a time-series database.
- **AI Engine** applies machine-learning models for anomaly detection, capacity forecasting, and root-cause analysis.
- **Visualization Layer** renders dashboards and status overviews through a web interface for operations teams.
- **Alerting Service** evaluates policy rules and distributes notifications to email, chat, and ticketing systems.

A typical deployment leverages container orchestration (e.g., Docker Compose or Kubernetes) to run each service independently while sharing the same message bus and data stores.

## Key Features
- **SNMP and ICMP Monitoring:** Poll devices using SNMPv2/v3 and perform ICMP reachability tests to track latency, jitter, and availability.
- **AI-driven Anomaly Detection:** Detect outliers and performance degradation by training models on historical metrics and live telemetry streams.
- **Interactive Dashboards:** Visualize device status, interface utilization, and traffic trends with real-time refresh and historical playback.
- **Automated Alerts:** Trigger threshold-based and behavior-based notifications with configurable escalation paths.

## Usage Examples
Run the collectors and analytics services locally:
```bash
make up
```

Inspect AI-detected anomalies via the command-line interface:
```bash
python cli.py anomalies --since 1h
```

Export a dashboard snapshot for reporting:
```bash
python tools/export_dashboard.py --id core-network --output reports/core-network.png
```

To stop all services and clean up containers:
```bash
make down
```
