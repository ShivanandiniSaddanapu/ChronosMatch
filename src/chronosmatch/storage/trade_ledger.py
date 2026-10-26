
import sqlite3
from pathlib import Path
from time import time_ns

from chronosmatch.matching.engine import Trade


class TradeLedger:
    """Persist executed trades in SQLite, supporting idempotent IPC events."""

    def __init__(self, database_path: str | Path):
        self._connection = sqlite3.connect(str(database_path))

        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                buy_order_id INTEGER NOT NULL,
                sell_order_id INTEGER NOT NULL,
                price REAL NOT NULL CHECK (price > 0),
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                recorded_at_ns INTEGER NOT NULL
            )
            """
        )

        # Event IDs are unique only for trades arriving through the
        # durable IPC event path. Legacy save_trades() remains unchanged.
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS trade_events (
                event_id INTEGER PRIMARY KEY,
                trade_id INTEGER NOT NULL UNIQUE,
                FOREIGN KEY (trade_id) REFERENCES trades(trade_id)
            )
            """
        )
        self._connection.commit()

    def save_trades(self, trades: list[Trade]) -> int:
        """Save a batch atomically. Identical executions remain distinct."""
        if not trades:
            return 0

        rows = [
            (
                trade.buy_order_id,
                trade.sell_order_id,
                trade.price,
                trade.quantity,
                time_ns(),
            )
            for trade in trades
        ]

        with self._connection:
            self._connection.executemany(
                """
                INSERT INTO trades (
                    buy_order_id,
                    sell_order_id,
                    price,
                    quantity,
                    recorded_at_ns
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                rows,
            )

        return len(rows)

    def save_events(self, events: list[tuple[int, Trade]]) -> int:
        """Persist trade events idempotently using their unique event IDs."""
        if not events:
            return 0

        saved = 0

        with self._connection:
            for event_id, trade in events:
                if event_id < 0:
                    raise ValueError("Event ID must not be negative")

                # Skip events that have already been persisted.
                existing = self._connection.execute(
                    "SELECT 1 FROM trade_events WHERE event_id = ?",
                    (event_id,),
                ).fetchone()

                if existing is not None:
                    continue

                cursor = self._connection.execute(
                    """
                    INSERT INTO trades (
                        buy_order_id,
                        sell_order_id,
                        price,
                        quantity,
                        recorded_at_ns
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        trade.buy_order_id,
                        trade.sell_order_id,
                        trade.price,
                        trade.quantity,
                        time_ns(),
                    ),
                )

                self._connection.execute(
                    """
                    INSERT INTO trade_events (event_id, trade_id)
                    VALUES (?, ?)
                    """,
                    (event_id, cursor.lastrowid),
                )

                saved += 1

        return saved

    def get_trades(self) -> list[Trade]:
        """Return all saved trades in insertion order."""
        rows = self._connection.execute(
            """
            SELECT buy_order_id, sell_order_id, price, quantity
            FROM trades
            ORDER BY trade_id
            """
        ).fetchall()

        return [
            Trade(
                buy_order_id=buy_order_id,
                sell_order_id=sell_order_id,
                price=price,
                quantity=quantity,
            )
            for buy_order_id, sell_order_id, price, quantity in rows
        ]

    def count(self) -> int:
        """Return the total number of saved trades."""
        row = self._connection.execute(
            "SELECT COUNT(*) FROM trades"
        ).fetchone()
        return row[0]

    def close(self) -> None:
        """Close the SQLite database connection."""
        self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
