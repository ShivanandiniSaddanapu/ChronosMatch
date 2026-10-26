
import asyncio
import sqlite3

import pytest

from chronosmatch.matching.engine import Trade
from chronosmatch.ipc.trade_ring_buffer import TradeMMapRingBuffer
from chronosmatch.storage.async_trade_flusher import AsyncTradeFlusher
from chronosmatch.storage.trade_ledger import TradeLedger


def make_trade(price=100.0, quantity=5):
    return Trade(
        buy_order_id=1,
        sell_order_id=2,
        price=price,
        quantity=quantity,
    )


def test_failed_database_write_keeps_events_pending(tmp_path):
    async def scenario():
        with TradeMMapRingBuffer(
            str(tmp_path / "trades.mmap"),
            capacity=4,
        ) as buffer:
            with TradeLedger(tmp_path / "trades.db") as ledger:
                buffer.write(200, make_trade())

                flusher = AsyncTradeFlusher(buffer, ledger)

                def fail_save(events):
                    raise sqlite3.OperationalError(
                        "simulated database failure"
                    )

                ledger.save_events = fail_save

                with pytest.raises(sqlite3.OperationalError):
                    await flusher.flush_once()

                assert buffer.count == 1
                assert ledger.count() == 0

    asyncio.run(scenario())
