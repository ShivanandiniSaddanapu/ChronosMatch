from chronosmatch.matching.order import Order, OrderSide
from chronosmatch.matching.order_book import OrderBook


def test_add_buy_order():
    book = OrderBook()

    order = Order.create(
        order_id=1,
        symbol="AAPL",
        side=OrderSide.BUY,
        price=100.0,
        quantity=10,
    )

    book.add(order)

    assert book.best_bid() == 100.0


def test_add_sell_order():
    book = OrderBook()

    order = Order.create(
        order_id=2,
        symbol="AAPL",
        side=OrderSide.SELL,
        price=101.0,
        quantity=5,
    )

    book.add(order)

    assert book.best_ask() == 101.0

def test_fifo_at_same_price():
    book = OrderBook()

    first_order = Order.create(
        order_id=1,
        symbol="AAPL",
        side=OrderSide.BUY,
        price=100.0,
        quantity=10,
    )

    second_order = Order.create(
        order_id=2,
        symbol="AAPL",
        side=OrderSide.BUY,
        price=100.0,
        quantity=20,
    )

    book.add(first_order)
    book.add(second_order)

    orders = book.bids[100.0]

    assert orders[0].order_id == 1
    assert orders[1].order_id == 2    



def test_best_bid_and_ask_follow_price_priority():
    book = OrderBook()

    buy_low = Order.create(
        order_id=1,
        symbol="AAPL",
        side=OrderSide.BUY,
        price=99.0,
        quantity=10,
    )

    buy_high = Order.create(
        order_id=2,
        symbol="AAPL",
        side=OrderSide.BUY,
        price=101.0,
        quantity=10,
    )

    sell_high = Order.create(
        order_id=3,
        symbol="AAPL",
        side=OrderSide.SELL,
        price=103.0,
        quantity=10,
    )

    sell_low = Order.create(
        order_id=4,
        symbol="AAPL",
        side=OrderSide.SELL,
        price=100.0,
        quantity=10,
    )

    book.add(buy_low)
    book.add(buy_high)
    book.add(sell_high)
    book.add(sell_low)

    assert book.best_bid() == 101.0
    assert book.best_ask() == 100.0    