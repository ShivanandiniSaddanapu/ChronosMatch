import cProfile
import pstats

from chronosmatch.matching.engine import MatchingEngine
from chronosmatch.matching.order import Order, OrderSide


def workload(number_of_orders: int = 50_000) -> None:
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


if __name__ == "__main__":
    profiler = cProfile.Profile()

    profiler.enable()
    workload()
    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")
    stats.print_stats(15)