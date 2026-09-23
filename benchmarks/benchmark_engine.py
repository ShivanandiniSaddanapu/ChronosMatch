import time

from chronosmatch.matching.cython_adapter import CythonMatchingAdapter
from chronosmatch.matching.engine import MatchingEngine
from chronosmatch.matching.order import Order, OrderSide


NUMBER_OF_ORDERS = 50_000
RUNS = 5


def matching_workload(engine, number_of_orders: int = NUMBER_OF_ORDERS) -> None:
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

        engine.submit(order)


def benchmark(name, engine_factory, runs: int = RUNS):
    results = []

    for _ in range(runs):
        engine = engine_factory()

        start = time.perf_counter()
        matching_workload(engine)
        elapsed = time.perf_counter() - start

        results.append(elapsed)

    average_time = sum(results) / len(results)
    throughput = NUMBER_OF_ORDERS / average_time

    print(f"=== {name} ===")
    print(f"Runs            : {runs}")
    print(f"Orders per run  : {NUMBER_OF_ORDERS:,}")
    print(f"Average time    : {average_time:.6f} seconds")
    print(f"Throughput      : {throughput:,.0f} orders/second")
    print()

    return average_time, throughput


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
