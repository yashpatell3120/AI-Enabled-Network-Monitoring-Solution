"""Command line entry point for the AI-enabled network monitoring toolkit."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from .alerting import AlertManager
from .anomaly import RollingZScoreDetector
from .config import MonitoringConfig, load_config
from .icmp import ICMPMonitor
from .pipeline import MonitoringPipeline
from .snmp import SNMPCollector


def _build_pipeline(config: MonitoringConfig) -> MonitoringPipeline:
    snmp_collector = SNMPCollector(config.snmp_metrics)
    icmp_monitor = ICMPMonitor(
        count=config.icmp.count,
        interval=config.icmp.interval,
        timeout=config.icmp.timeout,
    )
    detector = RollingZScoreDetector(
        threshold=config.anomaly.threshold,
        min_samples=config.anomaly.min_samples,
        window_size=config.anomaly.window_size,
    )
    alerts = AlertManager([lambda alert: print(alert.summary(), flush=True)])
    return MonitoringPipeline(
        snmp_collector=snmp_collector,
        icmp_monitor=icmp_monitor,
        detector=detector,
        alert_manager=alerts,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="Path to the monitoring YAML configuration file")
    parser.add_argument("--interval", type=float, default=60.0, help="Sampling interval in seconds")
    parser.add_argument("--once", action="store_true", help="Run a single iteration and exit")

    args = parser.parse_args(argv)
    config = load_config(args.config)
    pipeline = _build_pipeline(config)

    def run_once() -> None:
        snapshots = pipeline.sample_devices(config.devices)
        print(json.dumps([snapshot.to_dict() for snapshot in snapshots], indent=2))

    run_once()
    if args.once:
        return 0

    try:
        while True:
            time.sleep(args.interval)
            run_once()
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())

