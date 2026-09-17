import pytest

from chronosmatch.matching.order import Order, OrderSide


def test_create_buy_order():
    order = Order.create(
        order_id=1,
        symbol="AAPL",
        side=OrderSide.BUY,
        price=100.50,
        quantity=10,
    )

    assert order.order_id == 1
    assert order.symbol == "AAPL"
    assert order.side == OrderSide.BUY
    assert order.price == 100.50
    assert order.quantity == 10
    assert order.timestamp > 0


def test_order_rejects_zero_quantity():
    with pytest.raises(ValueError):
        Order.create(
            order_id=2,
            symbol="AAPL",
            side=OrderSide.BUY,
            price=100.0,
            quantity=0,
        )


def test_order_rejects_negative_quantity():
    with pytest.raises(ValueError):
        Order.create(
            order_id=3,
            symbol="AAPL",
            side=OrderSide.BUY,
            price=100.0,
            quantity=-5,
        )


def test_order_rejects_negative_price():
    with pytest.raises(ValueError):
        Order.create(
            order_id=4,
            symbol="AAPL",
            side=OrderSide.BUY,
            price=-100.0,
            quantity=10,
        )