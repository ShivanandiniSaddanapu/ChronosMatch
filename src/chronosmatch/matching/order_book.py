from collections import defaultdict, deque

from chronosmatch.matching.order import Order, OrderSide


class OrderBook:
    def __init__(self):
        self.bids = defaultdict(deque)
        self.asks = defaultdict(deque)

    def add(self, order: Order) -> None:
        if order.side == OrderSide.BUY:
            self.bids[order.price].append(order)
        else:
            self.asks[order.price].append(order)

    def best_bid(self):
        if not self.bids:
            return None
        return max(self.bids.keys())

    def best_ask(self):
        if not self.asks:
            return None
        return min(self.asks.keys())