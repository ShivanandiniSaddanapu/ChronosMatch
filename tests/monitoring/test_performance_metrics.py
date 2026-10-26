
import pytest

from chronosmatch.monitoring.performance_metrics import PerformanceMetrics


def test_records_order_and_trade_counts():
    metrics = PerformanceMetrics()

    metrics.record_submission(100, 2)
    metrics.record_submission(300, 1)

    assert metrics.orders_submitted == 2
    assert metrics.trades_executed == 3


def test_calculates_average_and_maximum_latency():
    metrics = PerformanceMetrics()

    metrics.record_submission(100, 1)
    metrics.record_submission(300, 0)

    assert metrics.average_latency_ns == 200
    assert metrics.max_latency_ns == 300


def test_empty_metrics_have_zero_latency():
    metrics = PerformanceMetrics()

    assert metrics.average_latency_ns == 0
    assert metrics.max_latency_ns == 0


@pytest.mark.parametrize(
    ("latency_ns", "trade_count"),
    [(-1, 0), (0, -1)],
)
def test_rejects_negative_values(latency_ns, trade_count):
    metrics = PerformanceMetrics()

    with pytest.raises(ValueError):
        metrics.record_submission(latency_ns, trade_count)
