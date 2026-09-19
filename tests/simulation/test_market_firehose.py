import asyncio

from chronosmatch.ipc.ring_buffer import MMapRingBuffer
from chronosmatch.simulation.market_firehose import MarketFirehose


def test_firehose_generates_orders(tmp_path):
    file_path = tmp_path / "firehose.mmap"

    buffer = MMapRingBuffer(
        str(file_path),
        capacity=10,
    )

    firehose = MarketFirehose(buffer)

    generated = asyncio.run(
        firehose.generate_orders(10)
    )

    assert generated == 10
    assert buffer.count == 10

    first_order = buffer.read()

    assert first_order == (1, 151.0, 11)

    buffer.close()


def test_firehose_generates_sequential_order_ids(tmp_path):
    file_path = tmp_path / "firehose.mmap"

    buffer = MMapRingBuffer(
        str(file_path),
        capacity=5,
    )

    firehose = MarketFirehose(
        buffer,
        start_order_id=100,
    )

    generated = asyncio.run(
        firehose.generate_orders(5)
    )

    assert generated == 5

    orders = [
        buffer.read()
        for _ in range(5)
    ]

    assert [order[0] for order in orders] == [
        100,
        101,
        102,
        103,
        104,
    ]

    buffer.close()


def test_firehose_writes_expected_price_and_quantity(tmp_path):
    file_path = tmp_path / "firehose.mmap"

    buffer = MMapRingBuffer(
        str(file_path),
        capacity=3,
    )

    firehose = MarketFirehose(buffer)

    asyncio.run(
        firehose.generate_orders(3)
    )

    assert buffer.read() == (1, 151.0, 11)
    assert buffer.read() == (2, 152.0, 12)
    assert buffer.read() == (3, 153.0, 13)

    buffer.close()