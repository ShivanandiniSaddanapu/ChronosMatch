
import json

from chronosmatch.matching.engine import Trade
from chronosmatch.monitoring.trade_logger import TradeLogger


def test_record_trade_writes_structured_json(tmp_path):
    log_path = tmp_path / "trades.jsonl"
    trade = Trade(
        buy_order_id=2,
        sell_order_id=1,
        price=100.0,
        quantity=5,
    )

    with TradeLogger(log_path) as audit:
        audit.record_trade(trade)

    event = json.loads(log_path.read_text(encoding="utf-8"))

    assert event["event"] == "trade_executed"
    assert event["buy_order_id"] == 2
    assert event["sell_order_id"] == 1
    assert event["price"] == 100.0
    assert event["quantity"] == 5
    assert isinstance(event["timestamp_ns"], int)


def test_record_multiple_trades(tmp_path):
    log_path = tmp_path / "trades.jsonl"
    trades = [
        Trade(2, 1, 100.0, 5),
        Trade(3, 4, 101.0, 2),
    ]

    with TradeLogger(log_path) as audit:
        assert audit.record_trades(trades) == 2

    events = [
        json.loads(line)
        for line in log_path.read_text(encoding="utf-8").splitlines()
    ]

    assert len(events) == 2
    assert events[0]["buy_order_id"] == 2
    assert events[1]["buy_order_id"] == 3
