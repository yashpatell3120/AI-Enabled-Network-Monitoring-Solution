"""Anomaly detection utilities for telemetry streams."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Deque, Dict, Optional

__all__ = ["AnomalyEvent", "RollingZScoreDetector"]


@dataclass(slots=True)
class AnomalyEvent:
    """Represents an anomalous observation detected in the telemetry."""

    metric: str
    value: float
    score: float
    mean: float
    stddev: float
    timestamp: datetime

    def to_dict(self) -> dict[str, float | str]:
        return {
            "metric": self.metric,
            "value": self.value,
            "score": self.score,
            "mean": self.mean,
            "stddev": self.stddev,
            "timestamp": self.timestamp.isoformat(),
        }


class RollingStatistics:
    """Keep a bounded history of values to compute statistics."""

    def __init__(self, window_size: int | None = None) -> None:
        self.window_size = window_size
        self._values: Deque[float] = deque(maxlen=window_size)

    def update(self, value: float) -> None:
        self._values.append(value)

    @property
    def count(self) -> int:
        return len(self._values)

    @property
    def mean(self) -> float:
        if not self._values:
            return 0.0
        return sum(self._values) / len(self._values)

    @property
    def stddev(self) -> float:
        if len(self._values) < 2:
            return 0.0
        mu = self.mean
        variance = sum((x - mu) ** 2 for x in self._values) / (len(self._values) - 1)
        return variance ** 0.5

class RollingZScoreDetector:
    """Detect anomalies using a rolling z-score algorithm."""

    def __init__(
        self,
        *,
        threshold: float = 3.0,
        min_samples: int = 10,
        window_size: int | None = 200,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._threshold = threshold
        self._min_samples = min_samples
        self._window_size = window_size
        self._clock: Callable[[], datetime] = clock or datetime.utcnow
        self._stats: Dict[str, RollingStatistics] = {}

    def process(self, metric: str, value: float) -> Optional[AnomalyEvent]:
        stats = self._stats.setdefault(metric, RollingStatistics(self._window_size))
        mean_before = stats.mean
        std_before = stats.stddev

        if stats.count < self._min_samples:
            stats.update(value)
            return None

        score = 0.0 if std_before == 0 else (value - mean_before) / std_before
        stats.update(value)
        if abs(score) < self._threshold:
            return None
        event = AnomalyEvent(
            metric=metric,
            value=value,
            score=score,
            mean=mean_before,
            stddev=std_before,
            timestamp=self._clock(),
        )
        return event

    def process_many(self, metrics: Dict[str, float]) -> list[AnomalyEvent]:
        events: list[AnomalyEvent] = []
        for name, value in metrics.items():
            event = self.process(name, value)
            if event is not None:
                events.append(event)
        return events

