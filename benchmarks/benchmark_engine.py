import time

from chronosmatch.matching.engine import MatchingEngine
from chronosmatch.matching.order import Order, OrderSide


def matching_workload(number_of_orders: int = 50_000) -> None:
    engine = MatchingEngine()

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


def order_book_workload(number_of_orders: int = 50_000) -> None:
    engine = MatchingEngine()

    for order_id in range(number_of_orders):
        order = Order.create(
            order_id=order_id,
            symbol="AAPL",
            side=OrderSide.BUY,
            price=100.0 + (order_id % 100),
            quantity=10,
        )

        engine.submit(order)


def benchmark(name, workload, runs=5):
    results = []

    for _ in range(runs):
        start = time.perf_counter()
        workload()
        elapsed = time.perf_counter() - start

        results.append(elapsed)

    average_time = sum(results) / len(results)
    throughput = 50_000 / average_time

    print(f"=== {name} ===")
    print(f"Runs            : {runs}")
    print(f"Orders per run  : 50,000")
    print(f"Average time    : {average_time:.6f} seconds")
    print(f"Throughput      : {throughput:,.0f} orders/second")
    print()


if __name__ == "__main__":
    benchmark(
        "Matching Workload",
        matching_workload,
    )

    benchmark(
        "Order Book Workload",
        order_book_workload,
    )