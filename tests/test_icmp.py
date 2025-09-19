from ai_network_monitoring.icmp import ICMPMonitor


def test_icmp_monitor_computes_statistics():
    def fake_ping(host, count, interval, timeout):
        assert host == "router"
        assert count == 4
        return [0.1, 0.2, 0.15, 0.12]

    monitor = ICMPMonitor(ping_func=fake_ping, count=4)
    result = monitor.probe("router")

    assert result.sent == 4
    assert result.received == 4
    assert abs(result.packet_loss) < 1e-6
    assert result.rtt_avg == sum([0.1, 0.2, 0.15, 0.12]) / 4
    assert result.jitter is not None


def test_icmp_monitor_handles_packet_loss():
    monitor = ICMPMonitor(ping_func=lambda *args, **kwargs: [0.1])
    result = monitor.probe("router")

    assert result.sent == 5
    assert result.received == 1
    assert result.packet_loss == 80.0

