"""Configuration helpers for the monitoring pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

from .snmp import SNMPDevice, SNMPMetric

__all__ = ["MonitoringConfig", "load_config"]


@dataclass(slots=True)
class ICMPConfig:
    count: int = 5
    interval: float = 1.0
    timeout: float = 1.0


@dataclass(slots=True)
class AnomalyConfig:
    threshold: float = 3.0
    min_samples: int = 20
    window_size: int | None = 200


@dataclass(slots=True)
class MonitoringConfig:
    devices: Sequence[SNMPDevice]
    snmp_metrics: Sequence[SNMPMetric]
    icmp: ICMPConfig
    anomaly: AnomalyConfig


def _parse_devices(entries: Iterable[dict]) -> List[SNMPDevice]:
    devices: List[SNMPDevice] = []
    for entry in entries:
        device = SNMPDevice(
            host=entry["host"],
            community=entry.get("community", "public"),
            port=entry.get("port", 161),
            version=entry.get("version", "2c"),
            extra={k: v for k, v in entry.items() if k not in {"host", "community", "port", "version"}},
        )
        devices.append(device)
    return devices


def _parse_metrics(entries: Iterable[dict]) -> List[SNMPMetric]:
    metrics: List[SNMPMetric] = []
    for entry in entries:
        metrics.append(
            SNMPMetric(
                name=entry["name"],
                oid=entry["oid"],
                scale=entry.get("scale", 1.0),
                offset=entry.get("offset", 0.0),
            )
        )
    return metrics


def load_config(path: str | Path) -> MonitoringConfig:
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ModuleNotFoundError(
            "PyYAML is required to load configuration files. Install it via 'pip install ai-network-monitoring'"
        ) from exc

    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    devices = _parse_devices(data.get("devices", []))
    metrics = _parse_metrics(data.get("snmp", {}).get("metrics", []))
    icmp_data = data.get("icmp", {})
    anomaly_data = data.get("anomaly", {})

    return MonitoringConfig(
        devices=devices,
        snmp_metrics=metrics,
        icmp=ICMPConfig(
            count=icmp_data.get("count", 5),
            interval=icmp_data.get("interval", 1.0),
            timeout=icmp_data.get("timeout", 1.0),
        ),
        anomaly=AnomalyConfig(
            threshold=anomaly_data.get("threshold", 3.0),
            min_samples=anomaly_data.get("min_samples", 20),
            window_size=anomaly_data.get("window_size"),
        ),
    )

