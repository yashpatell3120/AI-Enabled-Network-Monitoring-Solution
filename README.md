# AI-Enabled Network Monitoring Solution

This repository contains a prototype for an AI-assisted network monitoring
platform that combines SNMP and ICMP telemetry with lightweight anomaly
detection. The objective is to showcase how real-time visibility, proactive
alerts, and vendor-agnostic monitoring can be delivered in a modular manner.

## Key Features

- **Synthetic SNMP and ICMP collectors** that mimic bandwidth, utilisation, and
  health metrics across multi-vendor switches and routers.
- **Statistical anomaly detection** based on configurable baselines and
  tolerances, producing rich context for downstream analysis.
- **Alert management** that assigns severity based on anomaly magnitude and
  captures messages ready for dashboards or ITSM integrations.
- **Architecture documentation** that maps the prototype to a production-ready
  AI-enabled monitoring platform.

## Repository Structure

```
├── config
│   └── sample_config.json      # Example device configuration and baselines
├── docs
│   └── architecture.md         # Detailed solution blueprint
├── src
│   └── ai_monitoring
│       ├── __init__.py
│       ├── alerts.py           # Alert model and severity mapping
│       ├── anomaly.py          # Statistical anomaly detection utilities
│       ├── collectors.py       # Synthetic SNMP/ICMP collectors
│       └── main.py             # CLI entry point to run simulations
└── tests
    └── test_anomaly.py         # Unit tests for anomaly detection
```

## Getting Started

1. **Install dependencies (optional).** The prototype relies only on the Python
   standard library and `pytest` for testing. Activate a virtual environment if
   required.
2. **Run the simulation.**

   ```bash
   python run_simulation.py --config config/sample_config.json --iterations 5
   ```

   The command prints JSON containing the alerts generated during the synthetic
   polling cycles. Adjust `--anomaly-probability` or `--seed` to explore
   different scenarios.

   > **Tip:** Advanced users can run the module directly via
   > `PYTHONPATH=src python -m ai_monitoring.main ...` if they prefer not to use
   > the helper script.

3. **Execute the unit tests.**

   ```bash
   pytest
   ```

## Extending the Prototype

- Replace the synthetic collectors with real SNMP (e.g., `pysnmp`) and ICMP
  implementations.
- Feed collected metrics into a time-series database or event bus to support
  dashboards and streaming analytics.
- Swap out the statistical detector for advanced ML algorithms such as Isolation
  Forest or Prophet-based forecasting.
- Integrate the `AlertManager` with chatops, SIEM, or ticketing systems to drive
  automated remediation workflows.

## License

This project is provided as-is for demonstration purposes.
