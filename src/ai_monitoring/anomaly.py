"""Anomaly detection utilities for the monitoring prototype."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Dict, Iterable, Mapping

from .config import AnomalyConfig


@dataclass
class StatisticalDetector:
    """Per-metric statistical detector based on z-scores."""

    baseline: Iterable[float]
    z_threshold: float = 3.0
    min_std: float = 0.05
    absolute_tolerance: float = 0.0

    def __post_init__(self) -> None:
        self._history = list(self.baseline)
        if not self._history:
            raise ValueError("StatisticalDetector requires at least one baseline value")
        self.mean = mean(self._history)
        if len(self._history) > 1:
            self.std = max(pstdev(self._history), self.min_std)
        else:
            self.std = self.min_std

    def score(self, value: float) -> float:
        """Return the anomaly score (approximate z-score) for a value."""

        if self.std <= self.min_std:
            denominator = max(self.absolute_tolerance, self.min_std, abs(self.mean), 1.0)
            return (value - self.mean) / denominator
        return (value - self.mean) / self.std

    def is_anomalous(self, value: float) -> bool:
        """Determine whether a metric value is anomalous."""

        score = abs(self.score(value))
        return score >= self.z_threshold


class AnomalyDetector:
    """High level anomaly detection across multiple metrics."""

    def __init__(self, detectors: Mapping[str, StatisticalDetector]) -> None:
        self.detectors = dict(detectors)

    @classmethod
    def from_baselines(
        cls,
        baselines: Mapping[str, Iterable[float]],
        anomaly_config: AnomalyConfig,
    ) -> "AnomalyDetector":
        """Build detectors from baseline series and configuration."""

        detectors: Dict[str, StatisticalDetector] = {}
        for metric, history in baselines.items():
            if not history:
                continue
            detectors[metric] = StatisticalDetector(
                history,
                z_threshold=anomaly_config.z_threshold,
                min_std=anomaly_config.min_std,
                absolute_tolerance=anomaly_config.tolerance_for(metric),
            )
        return cls(detectors)

    def detect(self, metrics: Mapping[str, float]) -> Dict[str, Dict[str, float]]:
        """Return anomaly details for metrics considered anomalous."""

        anomalies: Dict[str, Dict[str, float]] = {}
        for metric, value in metrics.items():
            detector = self.detectors.get(metric)
            if not detector:
                continue
            score = detector.score(value)
            if detector.is_anomalous(value):
                anomalies[metric] = {
                    "value": value,
                    "mean": detector.mean,
                    "std": detector.std,
                    "z_score": score,
                }
        return anomalies
