
import pytest

from chronosmatch.ipc.trade_ring_buffer import TradeMMapRingBuffer
from chronosmatch.matching.engine import Trade


def make_trade(
    buy_order_id=10,
    sell_order_id=20,
    price=150.5,
    quantity=5,
):
    return Trade(
        buy_order_id=buy_order_id,
        sell_order_id=sell_order_id,
        price=price,
        quantity=quantity,
    )


def test_write_and_peek_trade(tmp_path):
    path = str(tmp_path / "trades.mmap")

    with TradeMMapRingBuffer(path, capacity=4) as buffer:
        buffer.write(0, make_trade())

        records = buffer.peek_batch()

        assert records == [(0, 10, 20, 150.5, 5)]
        assert buffer.count == 1


def test_peek_does_not_acknowledge_records(tmp_path):
    path = str(tmp_path / "trades.mmap")

    with TradeMMapRingBuffer(path, capacity=4) as buffer:
        buffer.write(0, make_trade())
        buffer.write(1, make_trade(buy_order_id=11))

        first_read = buffer.peek_batch()
        second_read = buffer.peek_batch()

        assert first_read == second_read
        assert buffer.count == 2


def test_acknowledge_removes_records_from_pending_batch(tmp_path):
    path = str(tmp_path / "trades.mmap")

    with TradeMMapRingBuffer(path, capacity=4) as buffer:
        buffer.write(0, make_trade())
        buffer.write(1, make_trade(buy_order_id=11))

        buffer.acknowledge(1)

        assert buffer.count == 1
        assert buffer.peek_batch() == [(1, 11, 20, 150.5, 5)]


def test_full_buffer_rejects_new_trade(tmp_path):
    path = str(tmp_path / "trades.mmap")

    with TradeMMapRingBuffer(path, capacity=1) as buffer:
        buffer.write(0, make_trade())

        with pytest.raises(BufferError):
            buffer.write(1, make_trade())


def test_invalid_trade_is_rejected(tmp_path):
    path = str(tmp_path / "trades.mmap")

    with TradeMMapRingBuffer(path, capacity=4) as buffer:
        with pytest.raises(ValueError):
            buffer.write(0, make_trade(price=-1))


def test_invalid_acknowledgement_is_rejected(tmp_path):
    path = str(tmp_path / "trades.mmap")

    with TradeMMapRingBuffer(path, capacity=4) as buffer:
        buffer.write(0, make_trade())

        with pytest.raises(ValueError):
            buffer.acknowledge(2)


def test_pending_records_survive_reopening(tmp_path):
    path = str(tmp_path / "trades.mmap")

    with TradeMMapRingBuffer(path, capacity=4) as buffer:
        buffer.write(0, make_trade())

    with TradeMMapRingBuffer(path, capacity=4) as reopened:
        assert reopened.peek_batch() == [(0, 10, 20, 150.5, 5)]
        assert reopened.count == 1


def test_wraparound_preserves_record_order(tmp_path):
    path = str(tmp_path / "trades.mmap")

    with TradeMMapRingBuffer(path, capacity=2) as buffer:
        buffer.write(0, make_trade(buy_order_id=10))
        buffer.write(1, make_trade(buy_order_id=11))
        buffer.acknowledge(2)

        buffer.write(2, make_trade(buy_order_id=12))
        buffer.write(3, make_trade(buy_order_id=13))

        assert [record[0] for record in buffer.peek_batch()] == [2, 3]
        assert [record[1] for record in buffer.peek_batch()] == [12, 13]
