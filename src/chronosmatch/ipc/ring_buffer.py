import mmap
import os
import struct


class MMapRingBuffer:
    HEADER_FORMAT = struct.Struct("<QQ")
    RECORD_FORMAT = struct.Struct("<QdQ")

    WRITE_INDEX_OFFSET = 0
    READ_INDEX_OFFSET = 8

    HEADER_SIZE = HEADER_FORMAT.size
    RECORD_SIZE = RECORD_FORMAT.size

    def __init__(self, file_path: str, capacity: int = 1024):
        if capacity <= 0:
            raise ValueError("Capacity must be greater than zero")

        self.file_path = file_path
        self.capacity = capacity
        self.size = self.HEADER_SIZE + (
            self.RECORD_SIZE * capacity
        )

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

        write_index, read_index = self._read_header()

        if write_index == 0 and read_index == 0:
            self._write_header(0, 0)

    def _read_header(self):
        return self.HEADER_FORMAT.unpack(
            self._mmap[: self.HEADER_SIZE]
        )

    def _write_header(
        self,
        write_index: int,
        read_index: int,
    ):
        self._mmap[
            : self.HEADER_SIZE
        ] = self.HEADER_FORMAT.pack(
            write_index,
            read_index,
        )

    def _set_write_index(self, value: int):
        self._mmap[
            self.WRITE_INDEX_OFFSET :
            self.WRITE_INDEX_OFFSET + 8
        ] = struct.pack("<Q", value)

    def _set_read_index(self, value: int):
        self._mmap[
            self.READ_INDEX_OFFSET :
            self.READ_INDEX_OFFSET + 8
        ] = struct.pack("<Q", value)

    @property
    def write_index(self) -> int:
        return struct.unpack(
            "<Q",
            self._mmap[
                self.WRITE_INDEX_OFFSET :
                self.WRITE_INDEX_OFFSET + 8
            ],
        )[0]

    @property
    def read_index(self) -> int:
        return struct.unpack(
            "<Q",
            self._mmap[
                self.READ_INDEX_OFFSET :
                self.READ_INDEX_OFFSET + 8
            ],
        )[0]

    @property
    def count(self) -> int:
        return self.write_index - self.read_index

    @property
    def is_empty(self) -> bool:
        return self.count == 0

    @property
    def is_full(self) -> bool:
        return self.count >= self.capacity

    def write(
        self,
        order_id: int,
        price: float,
        quantity: int,
    ) -> None:
        if self.is_full:
            raise BufferError("Ring buffer is full")

        if order_id < 0:
            raise ValueError(
                "Order ID must not be negative"
            )

        if price <= 0:
            raise ValueError(
                "Price must be greater than zero"
            )

        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )

        write_index = self.write_index

        offset = self.HEADER_SIZE + (
            write_index % self.capacity
        ) * self.RECORD_SIZE

        data = self.RECORD_FORMAT.pack(
            order_id,
            price,
            quantity,
        )

        self._mmap[
            offset : offset + self.RECORD_SIZE
        ] = data

        self._set_write_index(write_index + 1)

    def read(self):
        if self.is_empty:
            return None

        read_index = self.read_index

        offset = self.HEADER_SIZE + (
            read_index % self.capacity
        ) * self.RECORD_SIZE

        data = self._mmap[
            offset : offset + self.RECORD_SIZE
        ]

        self._set_read_index(read_index + 1)

        return self.RECORD_FORMAT.unpack(data)

    def close(self) -> None:
        self._mmap.flush()
        self._mmap.close()
        self._file.close()

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.close()