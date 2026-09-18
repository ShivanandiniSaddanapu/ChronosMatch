import time

from chronosmatch.matching.engine import MatchingEngine
from chronosmatch.matching.order import Order, OrderSide


def run_benchmark(num_levels=1_000):
    engine = MatchingEngine()

    # Build many ask price levels.
    for i in range(num_levels):
        order = Order.create(
            order_id=i + 1,
            symbol="AAPL",
            side=OrderSide.SELL,
            price=100.0 + i,
            quantity=10,
        )
        engine.submit(order)

    start = time.perf_counter()

    # Match against the best ask repeatedly.
    order_id = num_levels + 1

    for i in range(num_levels):
        order = Order.create(
            order_id=order_id,
            symbol="AAPL",
            side=OrderSide.BUY,
            price=2000.0,
            quantity=10,
        )
        order_id += 1

        engine.submit(order)

    elapsed = time.perf_counter() - start

    print(f"Price levels     : {num_levels:,}")
    print(f"Matching orders  : {num_levels:,}")
    print(f"Matching time    : {elapsed:.6f} seconds")
    print(f"Orders/second    : {num_levels / elapsed:,.2f}")


if __name__ == "__main__":
    run_benchmark()
