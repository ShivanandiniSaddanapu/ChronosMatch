from chronosmatch.matching.cython.match_core import CythonOrderBook
from chronosmatch.matching.engine import Trade
from chronosmatch.matching.order import Order, OrderSide


class CythonMatchingAdapter:
    """Adapter between the Python order model and the Cython matching engine."""

    def __init__(self, capacity: int = 1024):
        self.order_book = CythonOrderBook(capacity)

    def submit(self, order: Order) -> list[Trade]:
        side = 0 if order.side == OrderSide.BUY else 1

        trades = self.order_book.match_order(
            order.order_id,
            order.price,
            order.quantity,
            side,
        )

        return [
            Trade(
                buy_order_id=buy_order_id,
                sell_order_id=sell_order_id,
                price=price,
                quantity=quantity,
            )
            for buy_order_id, sell_order_id, quantity, price in trades
        ]

    def size(self) -> int:
        return self.order_book.size()
