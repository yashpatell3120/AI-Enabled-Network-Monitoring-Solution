"""ICMP probe utilities for network health monitoring."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Callable, Iterable, List

from .snmp import MissingDependencyError

__all__ = ["ICMPMonitor", "ICMPResult"]


@dataclass(slots=True)
class ICMPResult:
    """Statistics collected from ICMP echo requests."""

    host: str
    sent: int
    received: int
    latencies: List[float]

    @property
    def packet_loss(self) -> float:
        if self.sent == 0:
            return 100.0
        lost = self.sent - self.received
        return (lost / self.sent) * 100.0

    @property
    def rtt_avg(self) -> float | None:
        return mean(self.latencies) if self.latencies else None

    @property
    def rtt_min(self) -> float | None:
        return min(self.latencies) if self.latencies else None

    @property
    def rtt_max(self) -> float | None:
        return max(self.latencies) if self.latencies else None

    @property
    def jitter(self) -> float | None:
        if len(self.latencies) < 2:
            return None
        deltas = [abs(a - b) for a, b in zip(self.latencies[1:], self.latencies[:-1])]
        return mean(deltas)

    def to_metrics(self) -> dict[str, float | None]:
        return {
            "packet_loss": self.packet_loss,
            "rtt_avg": self.rtt_avg,
            "rtt_min": self.rtt_min,
            "rtt_max": self.rtt_max,
            "jitter": self.jitter,
        }


PingFunction = Callable[[str, int, float, float], Iterable[float]]


class ICMPMonitor:
    """Perform ICMP probes using a pluggable ping implementation."""

    def __init__(
        self,
        *,
        ping_func: PingFunction | None = None,
        count: int = 5,
        interval: float = 1.0,
        timeout: float = 1.0,
    ) -> None:
        self._ping = ping_func or _default_ping
        self._count = count
        self._interval = interval
        self._timeout = timeout

    def probe(self, host: str) -> ICMPResult:
        latencies = list(self._ping(host, self._count, self._interval, self._timeout))
        received = len(latencies)
        return ICMPResult(host=host, sent=self._count, received=received, latencies=latencies)


def _default_ping(host: str, count: int, interval: float, timeout: float) -> Iterable[float]:
    try:
        from pythonping import ping  # type: ignore
    except ImportError as exc:  # pragma: no cover - requires optional dependency
        raise MissingDependencyError(
            "pythonping is required for ICMP probing. Install it via 'pip install ai-network-monitoring[icmp]'"
        ) from exc

    response = ping(host, count=count, interval=interval, timeout=timeout, verbose=False)
    return [reply.time_elapsed_ms / 1000.0 for reply in response if reply.success]

