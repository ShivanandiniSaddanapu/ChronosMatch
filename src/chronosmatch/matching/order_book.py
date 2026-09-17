from collections import defaultdict, deque

from chronosmatch.matching.order import Order, OrderSide


class OrderBook:
    def __init__(self):
        self.bids = defaultdict(deque)
        self.asks = defaultdict(deque)

        self._best_bid = None
        self._best_ask = None

    def add(self, order: Order) -> None:
        if order.side == OrderSide.BUY:
            self.bids[order.price].append(order)

            if self._best_bid is None or order.price > self._best_bid:
                self._best_bid = order.price

        else:
            self.asks[order.price].append(order)

            if self._best_ask is None or order.price < self._best_ask:
                self._best_ask = order.price

    def best_bid(self):
        return self._best_bid

    def best_ask(self):
        return self._best_ask

    def remove_empty_bid_level(self, price: float) -> None:
        if price in self.bids and not self.bids[price]:
            del self.bids[price]

            if self._best_bid == price:
                self._best_bid = max(self.bids.keys()) if self.bids else None

    def remove_empty_ask_level(self, price: float) -> None:
        if price in self.asks and not self.asks[price]:
            del self.asks[price]

            if self._best_ask == price:
                self._best_ask = min(self.asks.keys()) if self.asks else None