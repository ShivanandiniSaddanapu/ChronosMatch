
from chronosmatch.dashboard.latency_dashboard import (
    build_demo_engine,
    detect_whale_sweep,
)
from chronosmatch.matching.engine import Trade
from chronosmatch.matching.order import Order, OrderSide


def test_demo_detects_whale_sweep_across_three_price_levels():
    engine = build_demo_engine()

    event = engine.last_whale_event

    assert event is not None
    assert event["order_id"] == 6
    assert event["side"] == "BUY"
    assert event["quantity"] == 150
    assert event["levels"] == 3
    assert event["prices"] == [150.0, 151.0, 152.0]


def test_single_price_level_is_not_a_multi_level_sweep():
    order = Order.create(10, "AAPL", OrderSide.BUY, 101.0, 10)
    trades = [
        Trade(
            buy_order_id=10,
            sell_order_id=1,
            price=100.0,
            quantity=10,
        )
    ]

    event = detect_whale_sweep(order, trades, submitted_quantity=10)

    assert event is None


def test_no_trades_produces_no_whale_event():
    order = Order.create(11, "AAPL", OrderSide.BUY, 101.0, 10)

    event = detect_whale_sweep(order, [], submitted_quantity=10)

    assert event is None
