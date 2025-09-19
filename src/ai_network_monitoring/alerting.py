"""Alert routing utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Sequence

from .anomaly import AnomalyEvent

__all__ = ["AlertManager", "Alert", "AlertSink"]

AlertSink = Callable[["Alert"], None]


@dataclass(slots=True)
class Alert:
    """Represents a notification triggered by one or more anomalies."""

    device: str
    anomalies: Sequence[AnomalyEvent]

    def summary(self) -> str:
        metrics = ", ".join(f"{event.metric} (z={event.score:.2f})" for event in self.anomalies)
        return f"Device {self.device} anomalies: {metrics}"


class AlertManager:
    """Dispatch anomalies to subscribed sinks."""

    def __init__(self, sinks: Iterable[AlertSink] | None = None) -> None:
        self._sinks: List[AlertSink] = list(sinks or [])

    def subscribe(self, sink: AlertSink) -> None:
        self._sinks.append(sink)

    def dispatch(self, alert: Alert) -> None:
        for sink in self._sinks:
            sink(alert)

    def dispatch_many(self, device: str, anomalies: Sequence[AnomalyEvent]) -> None:
        if not anomalies:
            return
        alert = Alert(device=device, anomalies=anomalies)
        self.dispatch(alert)

