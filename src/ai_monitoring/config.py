"""Configuration models and helpers for the monitoring prototype."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Sequence


@dataclass
class AnomalyConfig:
    """Configuration parameters for anomaly detection."""

    z_threshold: float = 3.0
    min_std: float = 0.05
    absolute_tolerance: Dict[str, float] = field(default_factory=dict)

    def tolerance_for(self, metric: str) -> float:
        """Return the absolute tolerance configured for a metric."""

        if metric in self.absolute_tolerance:
            return self.absolute_tolerance[metric]
        return self.absolute_tolerance.get("default", 0.0)


@dataclass
class DeviceConfig:
    """Representation of a monitored network device."""

    name: str
    ip_address: str
    vendor: str
    snmp: Dict[str, object] = field(default_factory=dict)
    icmp: Dict[str, object] = field(default_factory=dict)
    baselines: Dict[str, Sequence[float]] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def metric_names(self) -> List[str]:
        """Return the metrics configured for the device."""

        names = set()
        names.update(self.snmp.get("metrics", []))
        names.update(self.icmp.get("metrics", []))
        return sorted(names)


@dataclass
class MonitoringConfig:
    """Top-level configuration for the monitoring solution."""

    polling_interval_seconds: int
    anomaly: AnomalyConfig
    devices: List[DeviceConfig]


def _parse_device(device_data: Dict[str, object]) -> DeviceConfig:
    """Convert raw JSON device data into a :class:`DeviceConfig`."""

    return DeviceConfig(
        name=device_data["name"],
        ip_address=device_data["ip_address"],
        vendor=device_data["vendor"],
        snmp=device_data.get("snmp", {}),
        icmp=device_data.get("icmp", {}),
        baselines=device_data.get("baselines", {}),
        tags=device_data.get("tags", []),
    )


def load_config(path: Path | str) -> MonitoringConfig:
    """Load configuration from a JSON file."""

    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    anomaly_data = raw.get("anomaly", {})
    anomaly_cfg = AnomalyConfig(
        z_threshold=anomaly_data.get("z_threshold", 3.0),
        min_std=anomaly_data.get("min_std", 0.05),
        absolute_tolerance=anomaly_data.get("absolute_tolerance", {}),
    )

    devices = [_parse_device(entry) for entry in raw.get("devices", [])]

    return MonitoringConfig(
        polling_interval_seconds=raw.get("polling_interval_seconds", 60),
        anomaly=anomaly_cfg,
        devices=devices,
    )
