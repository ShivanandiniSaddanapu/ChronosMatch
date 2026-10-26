
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



def test_successful_flush_persists_and_acknowledges_events(tmp_path):
    async def scenario():
        with TradeMMapRingBuffer(
            str(tmp_path / "trades.mmap"),
            capacity=4,
        ) as buffer:
            with TradeLedger(tmp_path / "trades.db") as ledger:
                trade = make_trade(price=123.5, quantity=7)
                buffer.write(200, trade)

                flusher = AsyncTradeFlusher(buffer, ledger)

                flushed = await flusher.flush_once()

                assert flushed == 1
                assert buffer.count == 0
                assert ledger.count() == 1

                saved_events = ledger.get_events()
                assert len(saved_events) == 1

                event_id, saved_trade = saved_events[0]
                assert event_id == 200
                assert saved_trade.buy_order_id == 1
                assert saved_trade.sell_order_id == 2
                assert saved_trade.price == 123.5
                assert saved_trade.quantity == 7

    asyncio.run(scenario())





 
def test_successful_flush_persists_and_acknowledges_events(tmp_path):
    async def scenario():
        with TradeMMapRingBuffer(
            str(tmp_path / "trades.mmap"),
            capacity=4,
        ) as buffer:
            with TradeLedger(tmp_path / "trades.db") as ledger:
                trade = make_trade(price=123.5, quantity=7)
                buffer.write(200, trade)

                flusher = AsyncTradeFlusher(buffer, ledger)

                flushed = await flusher.flush_once()

                assert flushed == 1
                assert buffer.count == 0
                assert ledger.count() == 1

                saved_trades = ledger.get_trades()
                assert len(saved_trades) == 1

                saved_trade = saved_trades[0]
                assert saved_trade.buy_order_id == 1
                assert saved_trade.sell_order_id == 2
                assert saved_trade.price == 123.5
                assert saved_trade.quantity == 7

    asyncio.run(scenario())
   

