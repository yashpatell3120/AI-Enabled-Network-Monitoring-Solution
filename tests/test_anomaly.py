"""Unit tests for the statistical anomaly detector."""

from ai_monitoring.anomaly import AnomalyDetector, StatisticalDetector
from ai_monitoring.config import AnomalyConfig


def test_statistical_detector_identifies_outlier():
    detector = StatisticalDetector([10, 11, 9, 10, 10], z_threshold=3.0, min_std=0.1)
    assert not detector.is_anomalous(10)
    assert detector.is_anomalous(25)


def test_anomaly_detector_returns_metadata():
    baselines = {"cpu_utilization_pct": [40, 42, 38, 41, 39]}
    config = AnomalyConfig(z_threshold=2.5, min_std=0.5)
    detector = AnomalyDetector.from_baselines(baselines, config)
    anomalies = detector.detect({"cpu_utilization_pct": 55})
    assert "cpu_utilization_pct" in anomalies
    details = anomalies["cpu_utilization_pct"]
    assert {"value", "mean", "std", "z_score"} <= set(details.keys())
    assert details["value"] == 55
