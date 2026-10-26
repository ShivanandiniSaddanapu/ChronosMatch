

import time

from chronosmatch.matching.cython_adapter import CythonMatchingAdapter
from chronosmatch.matching.engine import MatchingEngine
from chronosmatch.matching.order import Order, OrderSide


NUMBER_OF_ORDERS = 50_000
RUNS = 5
NANOSECONDS_PER_SECOND = 1_000_000_000


def matching_workload(engine, number_of_orders: int = NUMBER_OF_ORDERS):
    total_latency_ns = 0
    min_latency_ns = None
    max_latency_ns = 0

    for order_id in range(number_of_orders):
        if order_id % 2 == 0:
            order = Order.create(
                order_id=order_id,
                symbol="AAPL",
                side=OrderSide.SELL,
                price=100.0,
                quantity=10,
            )
        else:
            order = Order.create(
                order_id=order_id,
                symbol="AAPL",
                side=OrderSide.BUY,
                price=100.0,
                quantity=10,
            )

        # Record the timestamp immediately before submission.
        entry_ns = time.perf_counter_ns()

        engine.submit(order)

        # Record the timestamp immediately after submission.
        exit_ns = time.perf_counter_ns()

        latency_ns = exit_ns - entry_ns
        total_latency_ns += latency_ns

        if min_latency_ns is None or latency_ns < min_latency_ns:
            min_latency_ns = latency_ns

        if latency_ns > max_latency_ns:
            max_latency_ns = latency_ns

    average_latency_ns = total_latency_ns / number_of_orders

    return average_latency_ns, min_latency_ns, max_latency_ns


def benchmark(name, engine_factory, runs: int = RUNS):
    elapsed_results_ns = []
    latency_results_ns = []

    for _ in range(runs):
        engine = engine_factory()

        # Measure the complete workload.
        start_ns = time.perf_counter_ns()

        average_latency_ns, min_latency_ns, max_latency_ns = (
            matching_workload(engine)
        )

        elapsed_ns = time.perf_counter_ns() - start_ns

        elapsed_results_ns.append(elapsed_ns)
        latency_results_ns.append(
            (average_latency_ns, min_latency_ns, max_latency_ns)
        )

    average_elapsed_ns = sum(elapsed_results_ns) / len(elapsed_results_ns)
    average_seconds = average_elapsed_ns / NANOSECONDS_PER_SECOND
    throughput = NUMBER_OF_ORDERS / average_seconds

    average_order_latency_ns = (
        sum(result[0] for result in latency_results_ns) / runs
    )
    minimum_order_latency_ns = min(
        result[1] for result in latency_results_ns
    )
    maximum_order_latency_ns = max(
        result[2] for result in latency_results_ns
    )

    print(f"=== {name} ===")
    print(f"Runs                       : {runs}")
    print(f"Orders per run             : {NUMBER_OF_ORDERS:,}")
    print(f"Average workload time      : {average_seconds:.6f} seconds")
    print(f"Average workload time      : {average_elapsed_ns:,.0f} nanoseconds")
    print(f"Average order latency      : {average_order_latency_ns:,.0f} nanoseconds")
    print(f"Minimum order latency      : {minimum_order_latency_ns:,} nanoseconds")
    print(f"Maximum order latency      : {maximum_order_latency_ns:,} nanoseconds")
    print(f"Throughput                 : {throughput:,.0f} orders/second")
    print()

    return average_seconds, throughput


if __name__ == "__main__":
    python_time, python_throughput = benchmark(
        "Python MatchingEngine",
        MatchingEngine,
    )

    cython_time, cython_throughput = benchmark(
        "Cython Matching Adapter",
        CythonMatchingAdapter,
    )

    speedup = python_time / cython_time

    print("=== Performance Comparison ===")
    print(f"Python throughput : {python_throughput:,.0f} orders/second")
    print(f"Cython throughput : {cython_throughput:,.0f} orders/second")
    print(f"Cython speedup    : {speedup:.2f}x")
