import mmap
import os
import struct


class MMapRingBuffer:
    RECORD_FORMAT = struct.Struct("<QdQ")
    RECORD_SIZE = RECORD_FORMAT.size

    def __init__(self, file_path: str, capacity: int = 1024):
        if capacity <= 0:
            raise ValueError("Capacity must be greater than zero")

        self.file_path = file_path
        self.capacity = capacity
        self.size = self.RECORD_SIZE * capacity

        self._file = open(file_path, "a+b")

        self._file.seek(0, os.SEEK_END)

        if self._file.tell() < self.size:
            self._file.truncate(self.size)

        self._file.flush()

        self._mmap = mmap.mmap(
            self._file.fileno(),
            self.size,
            access=mmap.ACCESS_WRITE,
        )

        self.write_index = 0
        self.read_index = 0

    @property
    def count(self) -> int:
        return self.write_index - self.read_index

    @property
    def is_empty(self) -> bool:
        return self.count == 0

    @property
    def is_full(self) -> bool:
        return self.count >= self.capacity

    def write(self, order_id: int, price: float, quantity: int) -> None:
        if self.is_full:
            raise BufferError("Ring buffer is full")

        if order_id < 0:
            raise ValueError("Order ID must not be negative")

        if price <= 0:
            raise ValueError("Price must be greater than zero")

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        offset = (
            self.write_index % self.capacity
        ) * self.RECORD_SIZE

        data = self.RECORD_FORMAT.pack(
            order_id,
            price,
            quantity,
        )

        self._mmap[offset : offset + self.RECORD_SIZE] = data

        self.write_index += 1

    def read(self):
        if self.is_empty:
            return None

        offset = (
            self.read_index % self.capacity
        ) * self.RECORD_SIZE

        data = self._mmap[
            offset : offset + self.RECORD_SIZE
        ]

        self.read_index += 1

        return self.RECORD_FORMAT.unpack(data)

    def close(self) -> None:
        self._mmap.flush()
        self._mmap.close()
        self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()