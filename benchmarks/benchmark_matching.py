
import statistics
import time

from chronosmatch.matching.cython_adapter import CythonMatchingAdapter
from chronosmatch.matching.engine import MatchingEngine
from chronosmatch.matching.order import Order, OrderSide


WARMUP_GROUPS = 500
MEASURED_GROUPS = 5_000
MEASURED_ROUNDS = 5


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


def run_benchmark(engine_name: str, engine, orders: list[Order]) -> dict:
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


def verify_equivalence(python_result: dict, cython_result: dict) -> None:
    """Verify identical trade executions and expected totals."""
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


def main() -> None:
    # Warm up each implementation with a fresh engine and fresh orders.
    for name, engine in (
        ("Python", MatchingEngine()),
        ("Cython", CythonMatchingAdapter(capacity=128)),
    ):
        for order in make_trade_heavy_orders(WARMUP_GROUPS):
            engine.submit(order)

        print(f"{name} warm-up completed.")

    results = {"Python": [], "Cython": []}

    for round_number in range(MEASURED_ROUNDS):
        # Alternate which implementation is measured first.
        if round_number % 2 == 0:
            order = ("Python", "Cython")
        else:
            order = ("Cython", "Python")

        round_results = {}

        for name in order:
            engine = (
                MatchingEngine()
                if name == "Python"
                else CythonMatchingAdapter(capacity=128)
            )

            result = run_benchmark(
                name,
                engine,
                make_trade_heavy_orders(MEASURED_GROUPS),
            )
            results[name].append(result)
            round_results[name] = result

        verify_equivalence(
            round_results["Python"],
            round_results["Cython"],
        )

        print(f"Round {round_number + 1}/{MEASURED_ROUNDS}: equivalence passed")

    print("\nChronosMatch Trade-Heavy Benchmark")
    print("=" * 70)
    print(f"Groups per engine per round: {MEASURED_GROUPS:,}")
    print(f"Measured rounds: {MEASURED_ROUNDS}")
    print("Execution order: alternated each round")

    summaries = {}

    for name in ("Python", "Cython"):
        runs = results[name]
        summaries[name] = {
            "throughput": statistics.median(
                result["throughput"] for result in runs
            ),
            "average_us": statistics.median(
                result["average_us"] for result in runs
            ),
            "p50_us": statistics.median(result["p50_us"] for result in runs),
            "p95_us": statistics.median(result["p95_us"] for result in runs),
            "p99_us": statistics.median(result["p99_us"] for result in runs),
        }

        summary = summaries[name]
        print(f"\n{name} engine (median across rounds)")
        print(f"Throughput:      {summary['throughput']:,.0f} orders/sec")
        print(f"Average latency: {summary['average_us']:.3f} us")
        print(f"p50 latency:     {summary['p50_us']:.3f} us")
        print(f"p95 latency:     {summary['p95_us']:.3f} us")
        print(f"p99 latency:     {summary['p99_us']:.3f} us")

    speedup = (
        summaries["Cython"]["throughput"]
        / summaries["Python"]["throughput"]
    )
    print(f"\nMedian throughput speedup: {speedup:.2f}x")
    print("Execution equivalence: PASSED for every measured round")
    print(f"Orders per engine per round: {MEASURED_GROUPS * 4:,}")
    print(f"Trades per engine per round: {MEASURED_GROUPS * 3:,}")
    print(f"Shares per engine per round: {MEASURED_GROUPS * 3:,}")


if __name__ == "__main__":
    main()
