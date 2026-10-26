
import statistics
import time

from chronosmatch.matching.cython_adapter import CythonMatchingAdapter
from chronosmatch.matching.engine import MatchingEngine
from chronosmatch.matching.order import Order, OrderSide


WARMUP_GROUPS = 500
MEASURED_GROUPS = 5_000


def make_trade_heavy_orders(groups: int) -> list[Order]:
    """Create groups of three sell orders swept by one buy order."""
    orders = []

    for group in range(groups):
        base_id = group * 4

        orders.append(
            Order.create(base_id + 1, "TEST", OrderSide.SELL, 100.0, 1)
        )
        orders.append(
            Order.create(base_id + 2, "TEST", OrderSide.SELL, 101.0, 1)
        )
        orders.append(
            Order.create(base_id + 3, "TEST", OrderSide.SELL, 102.0, 1)
        )
        orders.append(
            Order.create(base_id + 4, "TEST", OrderSide.BUY, 103.0, 3)
        )

    return orders


def percentile(values: list[int], percent: float) -> int:
    """Return a percentile from measured latencies."""
    ordered = sorted(values)
    index = round((percent / 100) * (len(ordered) - 1))
    return ordered[index]


def run_benchmark(
    engine_name: str,
    engine,
    orders: list[Order],
) -> dict:
    """Measure submission latency and collect executed trades."""
    latencies = []
    trade_count = 0
    total_quantity = 0
    trade_signature = []

    start_total = time.perf_counter_ns()

    for order in orders:
        start = time.perf_counter_ns()
        trades = engine.submit(order)
        latencies.append(time.perf_counter_ns() - start)

        trade_count += len(trades)

        for trade in trades:
            total_quantity += trade.quantity
            trade_signature.append(
                (
                    trade.buy_order_id,
                    trade.sell_order_id,
                    trade.price,
                    trade.quantity,
                )
            )

    elapsed_ns = time.perf_counter_ns() - start_total

    return {
        "engine": engine_name,
        "orders": len(orders),
        "trades": trade_count,
        "total_quantity": total_quantity,
        "trade_signature": trade_signature,
        "elapsed_ns": elapsed_ns,
        "throughput": len(orders) / (elapsed_ns / 1_000_000_000),
        "average_us": statistics.mean(latencies) / 1_000,
        "p50_us": percentile(latencies, 50) / 1_000,
        "p95_us": percentile(latencies, 95) / 1_000,
        "p99_us": percentile(latencies, 99) / 1_000,
    }


def main() -> None:
    # Warm up each engine using its own fresh Order objects.
    warmup_engines = (
        ("Python", MatchingEngine()),
        ("Cython", CythonMatchingAdapter(capacity=128)),
    )

    for name, engine in warmup_engines:
        warmup_orders = make_trade_heavy_orders(WARMUP_GROUPS)

        for order in warmup_orders:
            engine.submit(order)

        print(f"{name} warm-up completed.")

    # Benchmark each implementation with independent, fresh orders.
    python_result = run_benchmark(
        "Python",
        MatchingEngine(),
        make_trade_heavy_orders(MEASURED_GROUPS),
    )

    cython_result = run_benchmark(
        "Cython",
        CythonMatchingAdapter(capacity=128),
        make_trade_heavy_orders(MEASURED_GROUPS),
    )

    print("\nChronosMatch Trade-Heavy Benchmark")
    print("=" * 70)
    print("Matching scenario: 3 sell levels swept by each buy order")
    print(f"Groups per engine: {MEASURED_GROUPS:,}")

    for result in (python_result, cython_result):
        print(f"\n{result['engine']} engine")
        print(f"Orders submitted:    {result['orders']:,}")
        print(f"Trades executed:     {result['trades']:,}")
        print(f"Shares traded:       {result['total_quantity']:,}")
        print(f"Throughput:          {result['throughput']:,.0f} orders/sec")
        print(f"Average latency:     {result['average_us']:.3f} us")
        print(f"p50 latency:         {result['p50_us']:.3f} us")
        print(f"p95 latency:         {result['p95_us']:.3f} us")
        print(f"p99 latency:         {result['p99_us']:.3f} us")

    # Verify both engines generated identical executions.
    if python_result["trade_signature"] != cython_result["trade_signature"]:
        raise RuntimeError(
            "Python and Cython produced different trade executions."
        )

    expected_orders = MEASURED_GROUPS * 4
    expected_trades = MEASURED_GROUPS * 3
    expected_quantity = MEASURED_GROUPS * 3

    for result in (python_result, cython_result):
        if (
            result["orders"] != expected_orders
            or result["trades"] != expected_trades
            or result["total_quantity"] != expected_quantity
        ):
            raise RuntimeError(
                f"Unexpected trade totals for {result['engine']} engine."
            )

    print("\nExecution equivalence: PASSED")
    print(f"Expected orders: {expected_orders:,}")
    print(f"Expected trades: {expected_trades:,}")
    print(f"Expected shares: {expected_quantity:,}")


if __name__ == "__main__":
    main()
