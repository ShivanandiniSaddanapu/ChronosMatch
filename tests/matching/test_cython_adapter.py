from chronosmatch.matching.cython_adapter import CythonMatchingAdapter
from chronosmatch.matching.engine import Trade
from chronosmatch.matching.order import Order, OrderSide


def test_buy_matches_sell():
    adapter = CythonMatchingAdapter()

    adapter.submit(
        Order.create(
            1,
            "AAPL",
            OrderSide.SELL,
            100.0,
            50,
        )
    )

    trades = adapter.submit(
        Order.create(
            2,
            "AAPL",
            OrderSide.BUY,
            101.0,
            30,
        )
    )

    assert trades == [
        Trade(
            buy_order_id=2,
            sell_order_id=1,
            price=100.0,
            quantity=30,
        )
    ]

    assert adapter.size() == 1


def test_sell_matches_buy():
    adapter = CythonMatchingAdapter()

    adapter.submit(
        Order.create(
            1,
            "AAPL",
            OrderSide.BUY,
            100.0,
            50,
        )
    )

    trades = adapter.submit(
        Order.create(
            2,
            "AAPL",
            OrderSide.SELL,
            99.0,
            30,
        )
    )

    assert trades == [
        Trade(
            buy_order_id=1,
            sell_order_id=2,
            price=100.0,
            quantity=30,
        )
    ]

    assert adapter.size() == 1


def test_non_crossing_order_is_added():
    adapter = CythonMatchingAdapter()

    adapter.submit(
        Order.create(
            1,
            "AAPL",
            OrderSide.SELL,
            105.0,
            50,
        )
    )

    trades = adapter.submit(
        Order.create(
            2,
            "AAPL",
            OrderSide.BUY,
            100.0,
            50,
        )
    )

    assert trades == []
    assert adapter.size() == 2


def test_multiple_matches_are_converted_to_trades():
    adapter = CythonMatchingAdapter()

    adapter.submit(
        Order.create(
            1,
            "AAPL",
            OrderSide.SELL,
            100.0,
            50,
        )
    )

    adapter.submit(
        Order.create(
            2,
            "AAPL",
            OrderSide.SELL,
            101.0,
            75,
        )
    )

    trades = adapter.submit(
        Order.create(
            3,
            "AAPL",
            OrderSide.BUY,
            101.0,
            60,
        )
    )

    assert trades == [
        Trade(
            buy_order_id=3,
            sell_order_id=1,
            price=100.0,
            quantity=50,
        ),
        Trade(
            buy_order_id=3,
            sell_order_id=2,
            price=101.0,
            quantity=10,
        ),
    ]

    assert adapter.size() == 1
