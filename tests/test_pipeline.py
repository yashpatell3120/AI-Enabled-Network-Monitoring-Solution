from datetime import datetime

from ai_network_monitoring.alerting import AlertManager
from ai_network_monitoring.anomaly import RollingZScoreDetector
from ai_network_monitoring.icmp import ICMPMonitor
from ai_network_monitoring.pipeline import MonitoringPipeline
from ai_network_monitoring.snmp import SNMPCollector, SNMPDevice, SNMPMetric


def test_pipeline_detects_anomalies_and_dispatches_alerts():
    metrics = [SNMPMetric(name="cpu", oid="1")]

    values = iter([50.0, 50.5, 50.2, 99.0])

    def fake_fetcher(device, oids, timeout, retries):
        return {"1": next(values)}

    snmp = SNMPCollector(metrics, fetcher=fake_fetcher)
    icmp = ICMPMonitor(ping_func=lambda *args, **kwargs: [0.1, 0.2, 0.3])
    detector = RollingZScoreDetector(threshold=2.0, min_samples=3)

    received_alerts = []

    def record_alert(alert):
        received_alerts.append(alert)

    alerts = AlertManager([record_alert])
    pipeline = MonitoringPipeline(
        snmp_collector=snmp,
        icmp_monitor=icmp,
        detector=detector,
        alert_manager=alerts,
        clock=lambda: datetime(2024, 1, 1, 0, 0, 0),
    )

    device = SNMPDevice(host="switch")
    # Warm-up samples to build the baseline statistics
    pipeline.sample_device(device)
    pipeline.sample_device(device)
    pipeline.sample_device(device)
    snapshot = pipeline.sample_device(device)

    assert snapshot.device.host == "switch"
    assert "cpu" in snapshot.snmp_metrics
    assert received_alerts
    assert received_alerts[0].anomalies

