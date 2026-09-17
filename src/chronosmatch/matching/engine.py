from dataclasses import dataclass

from chronosmatch.matching.order import Order, OrderSide
from chronosmatch.matching.order_book import OrderBook


@dataclass(slots=True)
class Trade:
    buy_order_id: int
    sell_order_id: int
    price: float
    quantity: int


class MatchingEngine:
    def __init__(self):
        self.order_book = OrderBook()

    def submit(self, order: Order) -> list[Trade]:
        trades = []

        if order.side == OrderSide.BUY:
            trades.extend(self._match_buy(order))
        else:
            trades.extend(self._match_sell(order))

        if order.quantity > 0:
            self.order_book.add(order)

        return trades

    def _match_buy(self, order: Order) -> list[Trade]:
        trades = []


        while order.quantity > 0:
            best_price = self.order_book.best_ask()
            if best_price is None:
                break
            if order.price < best_price:
                break

       

            orders = self.order_book.asks[best_price]
            resting_order = orders[0]

            trade_quantity = min(order.quantity, resting_order.quantity)

            trades.append(
                Trade(
                    buy_order_id=order.order_id,
                    sell_order_id=resting_order.order_id,
                    price=resting_order.price,
                    quantity=trade_quantity,
                )
            )

            order.quantity -= trade_quantity
            resting_order.quantity -= trade_quantity

            if resting_order.quantity == 0:
                orders.popleft()

            if not orders:
                del self.order_book.asks[best_price]

        return trades

    def _match_sell(self, order: Order) -> list[Trade]:
        trades = []

        while order.quantity > 0 and self.order_book.best_bid() is not None:
            best_price = self.order_book.best_bid()

            if order.price > best_price:
                break

            orders = self.order_book.bids[best_price]
            resting_order = orders[0]

            trade_quantity = min(order.quantity, resting_order.quantity)

            trades.append(
                Trade(
                    buy_order_id=resting_order.order_id,
                    sell_order_id=order.order_id,
                    price=resting_order.price,
                    quantity=trade_quantity,
                )
            )

            order.quantity -= trade_quantity
            resting_order.quantity -= trade_quantity

            if resting_order.quantity == 0:
                orders.popleft()

            if not orders:
                del self.order_book.bids[best_price]

        return trades