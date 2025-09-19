from datetime import datetime, timedelta

from ai_network_monitoring.anomaly import RollingZScoreDetector


def test_detector_requires_min_samples():
    detector = RollingZScoreDetector(threshold=2.0, min_samples=3)
    assert detector.process("cpu", 10.0) is None
    assert detector.process("cpu", 11.0) is None
    assert detector.process("cpu", 10.5) is None


def test_detector_flags_outliers():
    times = iter(
        datetime(2024, 1, 1, 12, 0, 0) + timedelta(seconds=i)
        for i in range(10)
    )
    detector = RollingZScoreDetector(threshold=2.0, min_samples=3, clock=lambda: next(times))
    for value in [10.0, 10.5, 9.5, 10.2, 10.1, 9.8]:
        assert detector.process("cpu", value) is None

    event = detector.process("cpu", 20.0)
    assert event is not None
    assert event.metric == "cpu"
    assert event.value == 20.0
    assert event.score > 2.0
    assert event.timestamp.year == 2024

