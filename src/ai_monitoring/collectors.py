"""Simulated SNMP and ICMP collectors used by the prototype."""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from statistics import mean
from typing import Dict, Iterable

from .config import DeviceConfig

LOGGER = logging.getLogger(__name__)


@dataclass
class MetricSimulator:
    """Utility that generates synthetic metric samples."""

    random_source: random.Random
    noise_pct: float = 0.1
    anomaly_probability: float = 0.05
    anomaly_multiplier: float = 3.0

    def sample(self, baseline_values: Iterable[float]) -> float:
        """Generate a sample value around the supplied baseline."""

        history = list(baseline_values)
        if not history:
            raise ValueError("Baseline values are required to simulate metrics")

        baseline = mean(history)
        spread = abs(baseline) * self.noise_pct
        spread = max(spread, 0.01)
        value = baseline + self.random_source.uniform(-spread, spread)

        if self.random_source.random() < self.anomaly_probability:
            direction = 1 if self.random_source.random() < 0.5 else -1
            value = baseline + direction * spread * self.anomaly_multiplier
            LOGGER.debug(
                "Synthetic anomaly generated (baseline=%s, spread=%s, direction=%s)",
                baseline,
                spread,
                direction,
            )

        return max(value, 0.0)


class SNMPCollector:
    """Generate SNMP metrics for a device using synthetic data."""

    def __init__(
        self,
        rng: random.Random | None = None,
        default_noise_pct: float = 0.1,
        anomaly_probability: float = 0.05,
        anomaly_multiplier: float = 3.0,
    ) -> None:
        self.random = rng or random.Random()
        self.default_noise_pct = default_noise_pct
        self.anomaly_probability = anomaly_probability
        self.anomaly_multiplier = anomaly_multiplier

    def collect(self, device: DeviceConfig) -> Dict[str, float]:
        """Simulate SNMP metrics for the given device."""

        metrics: Dict[str, float] = {}
        snmp_cfg = device.snmp
        noise_pct = float(snmp_cfg.get("noise_pct", self.default_noise_pct))
        anomaly_probability = float(snmp_cfg.get("anomaly_probability", self.anomaly_probability))
        anomaly_multiplier = float(snmp_cfg.get("anomaly_multiplier", self.anomaly_multiplier))

        simulator = MetricSimulator(
            random_source=self.random,
            noise_pct=noise_pct,
            anomaly_probability=anomaly_probability,
            anomaly_multiplier=anomaly_multiplier,
        )

        for metric in snmp_cfg.get("metrics", []):
            baseline = device.baselines.get(metric)
            if not baseline:
                LOGGER.debug("No baseline provided for metric %s on %s", metric, device.name)
                continue
            try:
                value = simulator.sample(baseline)
            except ValueError:
                LOGGER.warning(
                    "Unable to simulate metric %s for %s due to empty baseline", metric, device.name
                )
                continue
            metrics[metric] = round(value, 3)
        return metrics


class ICMPProbe:
    """Generate ICMP health metrics using synthetic data."""

    def __init__(
        self,
        rng: random.Random | None = None,
        default_noise_pct: float = 0.05,
        anomaly_probability: float = 0.05,
        anomaly_multiplier: float = 5.0,
    ) -> None:
        self.random = rng or random.Random()
        self.default_noise_pct = default_noise_pct
        self.anomaly_probability = anomaly_probability
        self.anomaly_multiplier = anomaly_multiplier

    def probe(self, device: DeviceConfig) -> Dict[str, float]:
        """Simulate ICMP statistics for the provided device."""

        metrics: Dict[str, float] = {}
        icmp_cfg = device.icmp
        noise_pct = float(icmp_cfg.get("noise_pct", self.default_noise_pct))
        anomaly_probability = float(icmp_cfg.get("anomaly_probability", self.anomaly_probability))
        anomaly_multiplier = float(icmp_cfg.get("anomaly_multiplier", self.anomaly_multiplier))

        simulator = MetricSimulator(
            random_source=self.random,
            noise_pct=noise_pct,
            anomaly_probability=anomaly_probability,
            anomaly_multiplier=anomaly_multiplier,
        )

        for metric in icmp_cfg.get("metrics", []):
            baseline = device.baselines.get(metric)
            if not baseline:
                LOGGER.debug("No baseline provided for metric %s on %s", metric, device.name)
                continue
            try:
                value = simulator.sample(baseline)
            except ValueError:
                LOGGER.warning(
                    "Unable to simulate metric %s for %s due to empty baseline", metric, device.name
                )
                continue
            metrics[metric] = round(value, 3)
        return metrics
