"""SNMP data collection utilities.

The :class:`SNMPCollector` class offers a thin abstraction over ``pysnmp`` so
that production code can collect metrics while unit tests can inject in-memory
fixtures.  The module avoids importing third-party dependencies at import time;
``pysnmp`` is only imported when a collector attempts to perform a request. This
keeps the toolkit lightweight and enables environments without the optional
package to make use of the higher level orchestration components.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, Mapping, MutableMapping, Protocol

__all__ = [
    "MissingDependencyError",
    "SNMPCollector",
    "SNMPDevice",
    "SNMPMetric",
]


class MissingDependencyError(RuntimeError):
    """Raised when an optional dependency required for SNMP access is missing."""


class SNMPFetcher(Protocol):
    """Protocol for callables capable of fetching SNMP values."""

    def __call__(
        self,
        device: "SNMPDevice",
        oids: Iterable[str],
        *,
        timeout: float,
        retries: int,
    ) -> Mapping[str, Any]:
        ...


@dataclass(slots=True)
class SNMPMetric:
    """Configuration describing an SNMP metric to collect."""

    name: str
    oid: str
    scale: float = 1.0
    offset: float = 0.0
    transform: Callable[[Any], float] | None = None

    def convert(self, value: Any) -> float:
        """Convert a raw SNMP value to a floating point metric."""

        if self.transform is not None:
            value = self.transform(value)
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:  # pragma: no cover - defensive
            raise ValueError(
                f"Unable to convert SNMP value for metric '{self.name}'"
            ) from exc
        return numeric * self.scale + self.offset


@dataclass(slots=True)
class SNMPDevice:
    """Representation of a monitored network device."""

    host: str
    community: str = "public"
    port: int = 161
    version: str = "2c"
    extra: MutableMapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SNMPSample:
    """Container for collected SNMP metrics."""

    device: SNMPDevice
    metrics: Mapping[str, float]


class SNMPCollector:
    """Collect metrics from network devices via SNMP."""

    def __init__(
        self,
        metrics: Iterable[SNMPMetric],
        *,
        fetcher: SNMPFetcher | None = None,
        timeout: float = 1.0,
        retries: int = 1,
    ) -> None:
        self._metrics = list(metrics)
        self._fetcher = fetcher or _pysnmp_fetcher
        self._timeout = timeout
        self._retries = retries

    @property
    def metrics(self) -> tuple[SNMPMetric, ...]:
        return tuple(self._metrics)

    def collect(self, device: SNMPDevice) -> SNMPSample:
        """Collect all configured metrics for ``device``."""

        oid_to_metric: Dict[str, SNMPMetric] = {metric.oid: metric for metric in self._metrics}
        raw = self._fetcher(device, oid_to_metric.keys(), timeout=self._timeout, retries=self._retries)
        converted: Dict[str, float] = {}
        for oid, metric in oid_to_metric.items():
            if oid not in raw:
                continue
            converted[metric.name] = metric.convert(raw[oid])
        return SNMPSample(device=device, metrics=converted)


def _pysnmp_fetcher(
    device: SNMPDevice,
    oids: Iterable[str],
    *,
    timeout: float,
    retries: int,
) -> Mapping[str, Any]:
    """Default SNMP fetcher backed by :mod:`pysnmp`.

    The function is separated from :class:`SNMPCollector` to keep imports local
    and to allow the protocol to be swapped during tests.
    """

    try:
        from pysnmp.hlapi import (  # type: ignore
            CommunityData,
            ContextData,
            ObjectIdentity,
            ObjectType,
            SnmpEngine,
            UdpTransportTarget,
            getCmd,
        )
    except ImportError as exc:  # pragma: no cover - requires optional dependency
        raise MissingDependencyError(
            "pysnmp is required for SNMP collection. Install it via 'pip install ai-network-monitoring[snmp]'"
        ) from exc

    transport = UdpTransportTarget((device.host, device.port), timeout=timeout, retries=retries)
    community = CommunityData(device.community, mpModel=1 if device.version == "2c" else 0)
    context = ContextData()
    var_binds = [ObjectType(ObjectIdentity(oid)) for oid in oids]

    iterator = getCmd(SnmpEngine(), community, transport, context, *var_binds)
    error_indication, error_status, error_index, bindings = next(iterator)

    if error_indication:  # pragma: no cover - network specific
        raise RuntimeError(f"SNMP engine reported error: {error_indication}")
    if error_status:  # pragma: no cover - network specific
        index = int(error_index) - 1
        problematic = var_binds[index] if 0 <= index < len(var_binds) else "?"
        raise RuntimeError(
            f"SNMP error {error_status.prettyPrint()} at {problematic}"
        )

    results: Dict[str, Any] = {}
    for binding in bindings:
        oid, value = binding
        results[str(oid)] = value
    return results

