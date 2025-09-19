from ai_network_monitoring.snmp import SNMPCollector, SNMPDevice, SNMPMetric


def test_snmp_collector_converts_metrics():
    metrics = [
        SNMPMetric(name="cpu", oid="1", scale=0.5),
        SNMPMetric(name="memory", oid="2"),
    ]

    def fake_fetcher(device, oids, timeout, retries):
        assert device.host == "switch"
        assert set(oids) == {"1", "2"}
        return {"1": 10, "2": 42}

    collector = SNMPCollector(metrics, fetcher=fake_fetcher)
    sample = collector.collect(SNMPDevice(host="switch"))

    assert sample.metrics["cpu"] == 5.0
    assert sample.metrics["memory"] == 42.0
    assert sample.device.host == "switch"


def test_snmp_collector_missing_value_is_ignored():
    metrics = [SNMPMetric(name="cpu", oid="1")]

    collector = SNMPCollector(metrics, fetcher=lambda *args, **kwargs: {})
    sample = collector.collect(SNMPDevice(host="switch"))

    assert sample.metrics == {}

