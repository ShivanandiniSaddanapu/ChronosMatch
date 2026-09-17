from chronosmatch.matching.engine import MatchingEngine
from chronosmatch.matching.order import Order, OrderSide


def test_buy_matches_sell():
    engine = MatchingEngine()

    sell_order = Order.create(
        order_id=1,
        symbol="AAPL",
        side=OrderSide.SELL,
        price=100.0,
        quantity=10,
    )

    buy_order = Order.create(
        order_id=2,
        symbol="AAPL",
        side=OrderSide.BUY,
        price=101.0,
        quantity=5,
    )

    engine.submit(sell_order)
    trades = engine.submit(buy_order)

    assert len(trades) == 1
    assert trades[0].buy_order_id == 2
    assert trades[0].sell_order_id == 1
    assert trades[0].price == 100.0
    assert trades[0].quantity == 5



def test_partial_fill():
    engine = MatchingEngine()

    sell_order = Order.create(
        order_id=1,
        symbol="AAPL",
        side=OrderSide.SELL,
        price=100.0,
        quantity=10,
    )

    buy_order = Order.create(
        order_id=2,
        symbol="AAPL",
        side=OrderSide.BUY,
        price=101.0,
        quantity=5,
    )

    engine.submit(sell_order)
    trades = engine.submit(buy_order)

    assert len(trades) == 1
    assert trades[0].quantity == 5

    assert engine.order_book.best_ask() == 100.0
    assert engine.order_book.asks[100.0][0].quantity == 5



def test_multiple_price_levels():
    engine = MatchingEngine()

    first_sell = Order.create(
        order_id=1,
        symbol="AAPL",
        side=OrderSide.SELL,
        price=100.0,
        quantity=5,
    )

    second_sell = Order.create(
        order_id=2,
        symbol="AAPL",
        side=OrderSide.SELL,
        price=101.0,
        quantity=10,
    )

    buy_order = Order.create(
        order_id=3,
        symbol="AAPL",
        side=OrderSide.BUY,
        price=101.0,
        quantity=12,
    )

    engine.submit(first_sell)
    engine.submit(second_sell)

    trades = engine.submit(buy_order)

    assert len(trades) == 2

    assert trades[0].price == 100.0
    assert trades[0].quantity == 5

    assert trades[1].price == 101.0
    assert trades[1].quantity == 7

    assert engine.order_book.best_ask() == 101.0
    assert engine.order_book.asks[101.0][0].quantity == 3        


def test_sell_matches_multiple_price_levels():
    engine = MatchingEngine()

    first_buy = Order.create(
        order_id=1,
        symbol="AAPL",
        side=OrderSide.BUY,
        price=100.0,
        quantity=5,
    )

    second_buy = Order.create(
        order_id=2,
        symbol="AAPL",
        side=OrderSide.BUY,
        price=99.0,
        quantity=10,
    )

    sell_order = Order.create(
        order_id=3,
        symbol="AAPL",
        side=OrderSide.SELL,
        price=99.0,
        quantity=12,
    )

    engine.submit(first_buy)
    engine.submit(second_buy)

    trades = engine.submit(sell_order)

    assert len(trades) == 2

    assert trades[0].price == 100.0
    assert trades[0].quantity == 5

    assert trades[1].price == 99.0
    assert trades[1].quantity == 7

    assert engine.order_book.best_bid() == 99.0
    assert engine.order_book.bids[99.0][0].quantity == 3   



def test_unmatched_order_is_added_to_book():
    engine = MatchingEngine()

    sell_order = Order.create(
        order_id=1,
        symbol="AAPL",
        side=OrderSide.SELL,
        price=105.0,
        quantity=10,
    )

    buy_order = Order.create(
        order_id=2,
        symbol="AAPL",
        side=OrderSide.BUY,
        price=100.0,
        quantity=5,
    )

    engine.submit(sell_order)
    trades = engine.submit(buy_order)

    assert trades == []
    assert engine.order_book.best_bid() == 100.0
    assert engine.order_book.best_ask() == 105.0
    assert engine.order_book.bids[100.0][0].order_id == 2    