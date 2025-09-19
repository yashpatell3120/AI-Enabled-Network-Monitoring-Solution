"""High-level orchestration pipeline for network monitoring."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, Iterable, List

from .alerting import AlertManager
from .anomaly import AnomalyEvent, RollingZScoreDetector
from .icmp import ICMPMonitor
from .snmp import SNMPCollector, SNMPDevice

__all__ = ["MonitoringPipeline", "MonitoringSnapshot"]


@dataclass(slots=True)
class MonitoringSnapshot:
    """Aggregate telemetry collected for a device at a single timestamp."""

    device: SNMPDevice
    timestamp: datetime
    snmp_metrics: Dict[str, float]
    icmp_metrics: Dict[str, float | None]
    anomalies: List[AnomalyEvent]

    def to_dict(self) -> dict[str, object]:
        return {
            "device": {
                "host": self.device.host,
                "community": self.device.community,
                "port": self.device.port,
                "version": self.device.version,
            },
            "timestamp": self.timestamp.isoformat(),
            "snmp": self.snmp_metrics,
            "icmp": self.icmp_metrics,
            "anomalies": [event.to_dict() for event in self.anomalies],
        }


class MonitoringPipeline:
    """Coordinate data collection, anomaly detection, and alerting."""

    def __init__(
        self,
        *,
        snmp_collector: SNMPCollector,
        icmp_monitor: ICMPMonitor,
        detector: RollingZScoreDetector,
        alert_manager: AlertManager,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._snmp = snmp_collector
        self._icmp = icmp_monitor
        self._detector = detector
        self._alerts = alert_manager
        self._clock: Callable[[], datetime] = clock or datetime.utcnow

    def sample_device(self, device: SNMPDevice) -> MonitoringSnapshot:
        snmp_sample = self._snmp.collect(device)
        icmp_sample = self._icmp.probe(device.host)
        icmp_metrics = {k: v for k, v in icmp_sample.to_metrics().items() if v is not None}

        combined_metrics: Dict[str, float] = dict(snmp_sample.metrics)
        combined_metrics.update({k: float(v) for k, v in icmp_metrics.items()})
        anomalies = self._detector.process_many(combined_metrics)
        self._alerts.dispatch_many(device.host, anomalies)

        snapshot = MonitoringSnapshot(
            device=device,
            timestamp=self._clock(),
            snmp_metrics=snmp_sample.metrics,
            icmp_metrics=icmp_metrics,
            anomalies=anomalies,
        )
        return snapshot

    def sample_devices(self, devices: Iterable[SNMPDevice]) -> List[MonitoringSnapshot]:
        return [self.sample_device(device) for device in devices]

