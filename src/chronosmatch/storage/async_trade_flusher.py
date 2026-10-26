
import asyncio
import logging
from pathlib import Path

from chronosmatch.ipc.trade_ring_buffer import TradeMMapRingBuffer
from chronosmatch.matching.engine import Trade
from chronosmatch.storage.trade_ledger import TradeLedger

logger = logging.getLogger(__name__)


class AsyncTradeFlusher:
    """Persist pending mmap trade events to SQLite in background batches."""

    def __init__(
        self,
        buffer: TradeMMapRingBuffer,
        ledger: TradeLedger,
        batch_size: int = 100,
        poll_interval: float = 0.01,
    ):
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if poll_interval <= 0:
            raise ValueError("poll_interval must be positive")

        self.buffer = buffer
        self.ledger = ledger
        self.batch_size = batch_size
        self.poll_interval = poll_interval
        self._stop_event = asyncio.Event()

    async def flush_once(self) -> int:
        """Persist one batch, acknowledging only after a successful commit."""
        records = self.buffer.peek_batch(self.batch_size)

        if not records:
            return 0

        events = [
            (
                event_id,
                Trade(
                    buy_order_id=buy_order_id,
                    sell_order_id=sell_order_id,
                    price=price,
                    quantity=quantity,
                ),
            )
            for (
                event_id,
                buy_order_id,
                sell_order_id,
                price,
                quantity,
            ) in records
        ]

        # Run SQLite work off the event loop.
        self.ledger.save_events(events)

        # Only acknowledge after save_events has committed successfully.
        self.buffer.acknowledge(len(records))
        return len(records)

    async def run(self) -> None:
        """Flush continuously until stopped and all pending events are saved."""
        while not self._stop_event.is_set() or not self.buffer.is_empty:
            try:
                flushed = await self.flush_once()
            except Exception:
                logger.exception("Trade batch failed; events remain pending")
                await asyncio.sleep(self.poll_interval)
                continue

            if flushed == 0:
                await asyncio.sleep(self.poll_interval)

    def stop(self) -> None:
        """Request shutdown after pending events have been flushed."""
        self._stop_event.set()
