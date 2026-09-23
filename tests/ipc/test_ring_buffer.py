import multiprocessing as mp

from chronosmatch.ipc.ring_buffer import MMapRingBuffer


def test_write_and_read_order(tmp_path):
    file_path = tmp_path / "orders.mmap"

    buffer = MMapRingBuffer(str(file_path), capacity=4)

    buffer.write(101, 150.25, 50)

    assert buffer.read() == (101, 150.25, 50)
    assert buffer.read() is None

    buffer.close()


def test_multiple_orders(tmp_path):
    file_path = tmp_path / "orders.mmap"

    buffer = MMapRingBuffer(str(file_path), capacity=4)

    buffer.write(101, 150.25, 50)
    buffer.write(102, 151.75, 25)
    buffer.write(103, 152.50, 10)

    assert buffer.read() == (101, 150.25, 50)
    assert buffer.read() == (102, 151.75, 25)
    assert buffer.read() == (103, 152.50, 10)
    assert buffer.read() is None

    buffer.close()


def test_record_size(tmp_path):
    file_path = tmp_path / "orders.mmap"

    buffer = MMapRingBuffer(str(file_path), capacity=4)

    assert buffer.HEADER_SIZE == 16
    assert buffer.RECORD_SIZE == 24
    assert buffer.size == 112

    buffer.close()


def test_full_buffer_rejects_write(tmp_path):
    file_path = tmp_path / "orders.mmap"

    buffer = MMapRingBuffer(str(file_path), capacity=2)

    buffer.write(101, 150.25, 50)
    buffer.write(102, 151.75, 25)

    assert buffer.is_full
    assert buffer.count == 2

    try:
        buffer.write(103, 152.50, 10)
        assert False, "Expected BufferError"
    except BufferError:
        pass

    buffer.close()


def test_wrap_around(tmp_path):
    file_path = tmp_path / "orders.mmap"

    buffer = MMapRingBuffer(str(file_path), capacity=2)

    buffer.write(101, 150.25, 50)
    buffer.write(102, 151.75, 25)

    assert buffer.read() == (101, 150.25, 50)

    buffer.write(103, 152.50, 10)

    assert buffer.read() == (102, 151.75, 25)
    assert buffer.read() == (103, 152.50, 10)
    assert buffer.read() is None

    buffer.close()


def test_empty_and_count_state(tmp_path):
    file_path = tmp_path / "orders.mmap"

    buffer = MMapRingBuffer(str(file_path), capacity=4)

    assert buffer.is_empty
    assert not buffer.is_full
    assert buffer.count == 0

    buffer.write(101, 150.25, 50)

    assert not buffer.is_empty
    assert buffer.count == 1

    assert buffer.read() == (101, 150.25, 50)

    assert buffer.is_empty
    assert buffer.count == 0

    buffer.close()


def test_invalid_order_data(tmp_path):
    file_path = tmp_path / "orders.mmap"

    buffer = MMapRingBuffer(str(file_path), capacity=4)

    try:
        buffer.write(-1, 150.25, 50)
        assert False, "Expected ValueError"
    except ValueError:
        pass

    try:
        buffer.write(101, 0, 50)
        assert False, "Expected ValueError"
    except ValueError:
        pass

    try:
        buffer.write(101, 150.25, 0)
        assert False, "Expected ValueError"
    except ValueError:
        pass

    buffer.close()




def _ipc_consumer(file_path, result_queue):
    buffer = MMapRingBuffer(file_path, capacity=4)

    received = []

    while len(received) < 3:
        order = buffer.read()

        if order is not None:
            received.append(order)

    buffer.close()
    result_queue.put(received)


def test_shared_mmap_between_processes(tmp_path):
    file_path = str(tmp_path / "orders.mmap")

    buffer = MMapRingBuffer(file_path, capacity=4)
    buffer.close()

    result_queue = mp.Queue()

    consumer = mp.Process(
        target=_ipc_consumer,
        args=(file_path, result_queue),
    )

    consumer.start()

    buffer = MMapRingBuffer(file_path, capacity=4)

    buffer.write(101, 150.25, 50)
    buffer.write(102, 151.75, 25)
    buffer.write(103, 152.50, 10)

    buffer.close()

    consumer.join(timeout=5)

    assert consumer.exitcode == 0
    assert result_queue.get() == [
        (101, 150.25, 50),
        (102, 151.75, 25),
        (103, 152.50, 10),
    ]    