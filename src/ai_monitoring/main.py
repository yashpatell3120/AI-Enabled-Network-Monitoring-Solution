"""Command line entry point for the AI-enabled monitoring prototype."""

from __future__ import annotations

import argparse
import json
import logging
import random
from typing import Dict

from .alerts import AlertManager
from .anomaly import AnomalyDetector
from .collectors import ICMPProbe, SNMPCollector
from .config import MonitoringConfig, load_config

LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default="config/sample_config.json",
        help="Path to the monitoring configuration file",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of polling iterations to simulate",
    )
    parser.add_argument(
        "--anomaly-probability",
        type=float,
        default=0.15,
        help="Probability of synthetic anomalies per metric sample",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for reproducible simulations",
    )
    return parser.parse_args()


def build_detectors(config: MonitoringConfig) -> Dict[str, AnomalyDetector]:
    """Construct detectors for each device."""

    return {
        device.name: AnomalyDetector.from_baselines(device.baselines, config.anomaly)
        for device in config.devices
    }


def simulate_monitoring(
    config: MonitoringConfig,
    iterations: int,
    anomaly_probability: float,
    seed: int | None,
) -> Dict[str, object]:
    """Simulate multiple polling iterations and return alert data."""

    base_rng = random.Random(seed) if seed is not None else random.Random()
    snmp_rng = random.Random(base_rng.random())
    icmp_rng = random.Random(base_rng.random())
    snmp_collector = SNMPCollector(rng=snmp_rng, anomaly_probability=anomaly_probability)
    icmp_probe = ICMPProbe(rng=icmp_rng, anomaly_probability=anomaly_probability)
    detectors = build_detectors(config)
    alert_manager = AlertManager()

    for iteration in range(iterations):
        LOGGER.info("Starting iteration %s", iteration + 1)
        for device in config.devices:
            metrics = {}
            metrics.update(snmp_collector.collect(device))
            metrics.update(icmp_probe.probe(device))
            detector = detectors.get(device.name)
            if not detector:
                continue
            anomalies = detector.detect(metrics)
            if anomalies:
                alert_manager.create_alerts(device.name, anomalies)
                LOGGER.info("Anomalies detected on %s: %s", device.name, list(anomalies.keys()))
            else:
                LOGGER.debug("No anomalies detected on %s", device.name)
    return {
        "iterations": iterations,
        "alerts": [alert.as_dict() for alert in alert_manager.alerts],
    }


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    config = load_config(args.config)
    result = simulate_monitoring(
        config,
        iterations=args.iterations,
        anomaly_probability=args.anomaly_probability,
        seed=args.seed,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
