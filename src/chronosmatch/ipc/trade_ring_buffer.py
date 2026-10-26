
import mmap
import os
import struct


class TradeMMapRingBuffer:
    """Mmap ring buffer for completed trades with explicit acknowledgement."""

    HEADER_FORMAT = struct.Struct("<QQ")
    RECORD_FORMAT = struct.Struct("<QQQdQ")

    HEADER_SIZE = HEADER_FORMAT.size
    RECORD_SIZE = RECORD_FORMAT.size

    def __init__(self, file_path: str, capacity: int = 1024):
        if capacity <= 0:
            raise ValueError("Capacity must be greater than zero")

        self.file_path = file_path
        self.capacity = capacity
        self.size = self.HEADER_SIZE + self.RECORD_SIZE * capacity

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

        if write_index < read_index or write_index - read_index > capacity:
            self.close()
            raise ValueError("Invalid trade buffer header")

    def _read_header(self):
        return self.HEADER_FORMAT.unpack(
            self._mmap[:self.HEADER_SIZE]
        )

    @property
    def write_index(self):
        return struct.unpack_from("<Q", self._mmap, 0)[0]

    @property
    def read_index(self):
        return struct.unpack_from("<Q", self._mmap, 8)[0]

    @property
    def count(self):
        return self.write_index - self.read_index

    @property
    def is_empty(self):
        return self.count == 0

    @property
    def is_full(self):
        return self.count >= self.capacity

    def write(self, event_id, trade):
        if self.is_full:
            raise BufferError("Trade buffer is full")

        if event_id < 0:
            raise ValueError("Event ID must not be negative")
        if trade.buy_order_id < 0 or trade.sell_order_id < 0:
            raise ValueError("Order IDs must not be negative")
        if trade.price <= 0 or trade.quantity <= 0:
            raise ValueError("Trade price and quantity must be positive")

        index = self.write_index
        offset = self.HEADER_SIZE + (index % self.capacity) * self.RECORD_SIZE

        record = self.RECORD_FORMAT.pack(
            event_id,
            trade.buy_order_id,
            trade.sell_order_id,
            trade.price,
            trade.quantity,
        )
        self._mmap[offset:offset + self.RECORD_SIZE] = record

        # Publish the record only after its bytes have been written.
        struct.pack_into("<Q", self._mmap, 0, index + 1)

    def peek_batch(self, limit=100):
        """Read pending records without acknowledging or removing them."""
        if limit <= 0:
            raise ValueError("Limit must be greater than zero")

        start = self.read_index
        end = min(self.write_index, start + limit)
        records = []

        for index in range(start, end):
            offset = self.HEADER_SIZE + (index % self.capacity) * self.RECORD_SIZE
            records.append(
                self.RECORD_FORMAT.unpack(
                    self._mmap[offset:offset + self.RECORD_SIZE]
                )
            )

        return records

    def acknowledge(self, count):
        """Advance the read index after successful durable persistence."""
        if count < 0 or count > self.count:
            raise ValueError("Invalid acknowledgement count")

        struct.pack_into(
            "<Q",
            self._mmap,
            8,
            self.read_index + count,
        )

    def close(self):
        if not self._mmap.closed:
            self._mmap.flush()
            self._mmap.close()
        if not self._file.closed:
            self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
