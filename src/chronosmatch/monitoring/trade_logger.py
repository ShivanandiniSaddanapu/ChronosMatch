
import json
import logging
from pathlib import Path
from time import time_ns

from chronosmatch.matching.engine import Trade


class TradeLogger:
    """Write structured trade events to a log file."""

    def __init__(self, log_path: str | Path):
        self.logger = logging.getLogger(
            f"chronosmatch.trade_audit.{Path(log_path).resolve()}"
        )
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        # Avoid adding duplicate handlers if this logger is reused.
        if not self.logger.handlers:
            handler = logging.FileHandler(log_path, encoding="utf-8")
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(handler)

    def record_trade(self, trade: Trade) -> None:
        """Record one executed trade as a JSON line."""
        event = {
            "event": "trade_executed",
            "timestamp_ns": time_ns(),
            "buy_order_id": trade.buy_order_id,
            "sell_order_id": trade.sell_order_id,
            "price": trade.price,
            "quantity": trade.quantity,
        }

        self.logger.info(json.dumps(event, separators=(",", ":")))

    def record_trades(self, trades: list[Trade]) -> int:
        """Record a batch of trades and return the number recorded."""
        for trade in trades:
            self.record_trade(trade)

        return len(trades)

    def close(self) -> None:
        """Close this logger's file handlers."""
        for handler in self.logger.handlers[:]:
            handler.flush()
            handler.close()
            self.logger.removeHandler(handler)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
