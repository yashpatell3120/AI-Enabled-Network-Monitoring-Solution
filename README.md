# AI-Enabled Network Monitoring Solution

This project provides a modular Python toolkit for building an AI-enabled
network monitoring platform. It focuses on collecting SNMP and ICMP telemetry,
performing lightweight anomaly detection, and orchestrating alerts so network
operators can respond proactively to performance or security issues.

## Features

- **Vendor-agnostic SNMP collection** with configurable metrics and extensible
  fetchers.
- **ICMP-based network health checks** that compute latency, jitter, and packet
  loss statistics.
- **Rolling z-score anomaly detection** for identifying abnormal behavior in
  telemetry streams.
- **Alert orchestration pipeline** that unifies SNMP, ICMP, and anomaly insights
  into actionable notifications.
- **Configurable CLI** to run monitoring loops based on YAML configuration files.

## Project Layout

```
├── configs/               # Example configuration files
├── src/ai_network_monitoring/
│   ├── anomaly.py         # Rolling statistical anomaly detector
│   ├── alerting.py        # Alert routing abstractions
│   ├── cli.py             # Command line entry point
│   ├── config.py          # YAML configuration loader
│   ├── icmp.py            # ICMP probing utilities
│   ├── pipeline.py        # Monitoring orchestration pipeline
│   └── snmp.py            # SNMP collection primitives
└── tests/                 # Unit tests for the toolkit
```

## Getting Started

### Prerequisites

- Python 3.10+
- Optional runtime dependencies:
  - [`pysnmp`](https://pysnmp.readthedocs.io/) for SNMP access.
  - [`pythonping`](https://github.com/alessandromaggio/pythonping) for ICMP
    probing.

### Installation

Install the project and optional extras in a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
# Optional extras for full functionality
pip install .[snmp,icmp]
```

### Running the CLI

Use the provided sample configuration as a starting point:

```bash
python -m ai_network_monitoring.cli configs/sample_config.yaml --once
```

The CLI prints collected telemetry and any detected anomalies as JSON. When run
without `--once`, it continuously samples using the interval specified by
`--interval` (default: 60 seconds).

## Testing

Install the development dependencies and run the unit test suite:

```bash
pip install .[dev]
pytest
```

## Extending the Toolkit

- Add additional SNMP metrics by updating the configuration file or extending
  `SNMPMetric` with custom conversion logic.
- Implement alternative ICMP probing strategies by providing a custom
  `ping_func` to `ICMPMonitor`.
- Integrate other anomaly detection techniques by creating new detector classes
  that emit `AnomalyEvent` instances.
- Hook the `AlertManager` into chat, ticketing, or incident management systems.

## License

This project is released under the MIT License.

