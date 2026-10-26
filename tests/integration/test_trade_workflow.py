
import json

from chronosmatch.matching.engine import MatchingEngine
from chronosmatch.matching.order import Order, OrderSide
from chronosmatch.monitoring.trade_logger import TradeLogger
from chronosmatch.storage.trade_ledger import TradeLedger


def test_matching_trade_is_saved_and_audited(tmp_path):
    database_path = tmp_path / "trades.db"
    audit_path = tmp_path / "trades.jsonl"

    engine = MatchingEngine()

    # First, place a sell order in the order book.
    sell_order = Order.create(
        order_id=1,
        symbol="AAPL",
        side=OrderSide.SELL,
        price=100.0,
        quantity=5,
    )
    assert engine.submit(sell_order) == []

    # Then submit a buy order that matches the resting sell order.
    buy_order = Order.create(
        order_id=2,
        symbol="AAPL",
        side=OrderSide.BUY,
        price=100.0,
        quantity=5,
    )
    trades = engine.submit(buy_order)

    assert len(trades) == 1
    assert trades[0].buy_order_id == 2
    assert trades[0].sell_order_id == 1
    assert trades[0].price == 100.0
    assert trades[0].quantity == 5

    # Persist the execution and record its audit event.
    with TradeLedger(database_path) as ledger:
        assert ledger.save_trades(trades) == 1
        assert ledger.get_trades() == trades

    with TradeLogger(audit_path) as audit:
        assert audit.record_trades(trades) == 1

    # Verify the audit file contains the same trade details.
    events = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
    ]

    assert len(events) == 1
    assert events[0]["event"] == "trade_executed"
    assert events[0]["buy_order_id"] == 2
    assert events[0]["sell_order_id"] == 1
    assert events[0]["price"] == 100.0
    assert events[0]["quantity"] == 5
