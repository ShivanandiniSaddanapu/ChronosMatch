
class PerformanceMetrics:
    """Track observed order submissions and matching latency."""

    def __init__(self):
        self.orders_submitted = 0
        self.trades_executed = 0
        self.total_latency_ns = 0
        self.max_latency_ns = 0

    def record_submission(
        self,
        latency_ns: int,
        trade_count: int,
    ) -> None:
        """Record the measured latency and trades for one submission."""
        if latency_ns < 0:
            raise ValueError("Latency cannot be negative")

        if trade_count < 0:
            raise ValueError("Trade count cannot be negative")

        self.orders_submitted += 1
        self.trades_executed += trade_count
        self.total_latency_ns += latency_ns
        self.max_latency_ns = max(self.max_latency_ns, latency_ns)

    @property
    def average_latency_ns(self) -> float:
        """Average observed latency in nanoseconds."""
        if self.orders_submitted == 0:
            return 0.0

        return self.total_latency_ns / self.orders_submitted
