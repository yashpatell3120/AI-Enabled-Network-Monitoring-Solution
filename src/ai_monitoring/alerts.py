"""Alerting helpers for the AI-enabled monitoring prototype."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List


@dataclass
class Alert:
    """A simple representation of an alert raised by anomaly detection."""

    device: str
    metric: str
    value: float
    baseline_mean: float
    z_score: float
    severity: str
    message: str

    def as_dict(self) -> Dict[str, object]:
        """Convert the alert to a serialisable dictionary."""

        return asdict(self)


class AlertManager:
    """Collect alerts and apply severity thresholds."""

    def __init__(self) -> None:
        self._alerts: List[Alert] = []

    def create_alerts(self, device_name: str, anomalies: Dict[str, Dict[str, float]]) -> None:
        """Generate :class:`Alert` objects for anomaly results."""

        for metric, details in anomalies.items():
            severity = self._severity_from_z(details["z_score"])
            direction = "above" if details["z_score"] > 0 else "below"
            message = (
                f"{metric} deviated {direction} baseline on {device_name}: "
                f"value={details['value']} mean={details['mean']:.2f}"
            )
            self._alerts.append(
                Alert(
                    device=device_name,
                    metric=metric,
                    value=details["value"],
                    baseline_mean=details["mean"],
                    z_score=details["z_score"],
                    severity=severity,
                    message=message,
                )
            )

    def _severity_from_z(self, z_score: float) -> str:
        magnitude = abs(z_score)
        if magnitude >= 5:
            return "critical"
        if magnitude >= 4:
            return "major"
        if magnitude >= 3:
            return "minor"
        return "informational"

    @property
    def alerts(self) -> Iterable[Alert]:
        """Return the alerts collected so far."""

        return list(self._alerts)

    def clear(self) -> None:
        """Remove previously recorded alerts."""

        self._alerts.clear()
