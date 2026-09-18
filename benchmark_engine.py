import time

from chronosmatch.matching.engine import MatchingEngine
from chronosmatch.matching.order import Order, OrderSide


def run_benchmark(num_orders=10_000):
    engine = MatchingEngine()

    start = time.perf_counter()

    order_id = 1

    for i in range(num_orders):
        sell = Order.create(
            order_id=order_id,
            symbol="AAPL",
            side=OrderSide.SELL,
            price=100.0,
            quantity=10,
        )
        order_id += 1

        engine.submit(sell)

        buy = Order.create(
            order_id=order_id,
            symbol="AAPL",
            side=OrderSide.BUY,
            price=100.0,
            quantity=10,
        )
        order_id += 1

        engine.submit(buy)

    elapsed = time.perf_counter() - start

    print(f"Orders submitted : {num_orders * 2:,}")
    print(f"Total time       : {elapsed:.6f} seconds")
    print(f"Orders/second    : {(num_orders * 2) / elapsed:,.2f}")


if __name__ == "__main__":
    run_benchmark()
