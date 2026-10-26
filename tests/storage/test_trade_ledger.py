
import sqlite3

import pytest

from chronosmatch.matching.engine import Trade
from chronosmatch.storage.trade_ledger import TradeLedger


def make_trade(
    buy_order_id=2,
    sell_order_id=1,
    price=100.0,
    quantity=5,
):
    return Trade(
        buy_order_id=buy_order_id,
        sell_order_id=sell_order_id,
        price=price,
        quantity=quantity,
    )


def test_save_and_read_trade(tmp_path):
    database = tmp_path / "trades.db"

    with TradeLedger(database) as ledger:
        trade = make_trade()

        assert ledger.save_trades([trade]) == 1
        assert ledger.count() == 1
        assert ledger.get_trades() == [trade]


def test_save_multiple_trades_in_order(tmp_path):
    database = tmp_path / "trades.db"
    first = make_trade(quantity=5)
    second = make_trade(
        buy_order_id=3,
        sell_order_id=4,
        price=101.0,
        quantity=2,
    )

    with TradeLedger(database) as ledger:
        assert ledger.save_trades([first, second]) == 2
        assert ledger.get_trades() == [first, second]


def test_trades_survive_database_reopen(tmp_path):
    database = tmp_path / "trades.db"
    trade = make_trade()

    with TradeLedger(database) as ledger:
        ledger.save_trades([trade])

    with TradeLedger(database) as ledger:
        assert ledger.count() == 1
        assert ledger.get_trades() == [trade]


def test_saving_empty_batch_does_nothing(tmp_path):
    with TradeLedger(tmp_path / "trades.db") as ledger:
        assert ledger.save_trades([]) == 0
        assert ledger.count() == 0


def test_same_trade_can_be_saved_as_separate_execution(tmp_path):
    trade = make_trade()

    with TradeLedger(tmp_path / "trades.db") as ledger:
        assert ledger.save_trades([trade, trade]) == 2
        assert ledger.count() == 2


def test_invalid_trade_is_rejected_by_database(tmp_path):
    database = tmp_path / "trades.db"
    invalid_trade = make_trade(price=0.0)

    with TradeLedger(database) as ledger:
        with pytest.raises(sqlite3.IntegrityError):
            ledger.save_trades([invalid_trade])

        assert ledger.count() == 0


def test_failed_batch_does_not_save_partial_trades(tmp_path):
    database = tmp_path / "trades.db"
    valid_trade = make_trade()
    invalid_trade = make_trade(
        buy_order_id=3,
        sell_order_id=4,
        quantity=0,
    )

    with TradeLedger(database) as ledger:
        with pytest.raises(sqlite3.IntegrityError):
            ledger.save_trades([valid_trade, invalid_trade])

        # The entire batch should roll back.
        assert ledger.count() == 0


def test_same_event_id_is_not_saved_twice(tmp_path):
    database = tmp_path / "trades.db"
    trade = make_trade()

    with TradeLedger(database) as ledger:
        assert ledger.save_events([(42, trade)]) == 1
        assert ledger.save_events([(42, trade)]) == 0
        assert ledger.count() == 1


def test_different_event_ids_can_save_identical_trades(tmp_path):
    database = tmp_path / "trades.db"
    trade = make_trade()

    with TradeLedger(database) as ledger:
        assert ledger.save_events([(42, trade), (43, trade)]) == 2
        assert ledger.count() == 2


def test_failed_event_batch_rolls_back(tmp_path):
    database = tmp_path / "trades.db"
    valid_trade = make_trade()
    invalid_trade = make_trade(price=0)

    with TradeLedger(database) as ledger:
        with pytest.raises(sqlite3.IntegrityError):
            ledger.save_events([
                (100, valid_trade),
                (101, invalid_trade),
            ])

        assert ledger.count() == 0
        assert ledger.save_events([(100, valid_trade)]) == 1
