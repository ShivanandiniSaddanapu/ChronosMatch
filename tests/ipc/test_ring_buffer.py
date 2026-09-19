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

    assert buffer.RECORD_SIZE == 24
    assert buffer.size == 96

    buffer.close()