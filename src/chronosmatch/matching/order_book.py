import heapq
from collections import defaultdict, deque

from chronosmatch.matching.order import Order, OrderSide


class OrderBook:
    def __init__(self):
        self.bids = defaultdict(deque)
        self.asks = defaultdict(deque)

        # Max-heap for bids is implemented using negative prices.
        self._bid_prices = []

        # Min-heap for asks.
        self._ask_prices = []

    def add(self, order: Order) -> None:
        if order.side == OrderSide.BUY:
            if order.price not in self.bids:
                heapq.heappush(self._bid_prices, -order.price)

            self.bids[order.price].append(order)

        else:
            if order.price not in self.asks:
                heapq.heappush(self._ask_prices, order.price)

            self.asks[order.price].append(order)

    def best_bid(self):
        while self._bid_prices:
            price = -self._bid_prices[0]

            if price in self.bids:
                return price

            heapq.heappop(self._bid_prices)

        return None

    def best_ask(self):
        while self._ask_prices:
            price = self._ask_prices[0]

            if price in self.asks:
                return price

            heapq.heappop(self._ask_prices)

        return None