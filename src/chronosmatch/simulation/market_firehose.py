import asyncio
import time

from chronosmatch.ipc.ring_buffer import MMapRingBuffer


class MarketFirehose:
    def __init__(
        self,
        buffer: MMapRingBuffer,
        symbol: str = "AAPL",
        start_order_id: int = 1,
    ):
        self.buffer = buffer
        self.symbol = symbol
        self.next_order_id = start_order_id

    async def generate_orders(self, count: int) -> int:
        generated = 0

        while generated < count:
            order_id = self.next_order_id

            price = 150.0 + (order_id % 100)
            quantity = 10 + (order_id % 90)

            self.buffer.write(
                order_id,
                price,
                quantity,
            )

            self.next_order_id += 1
            generated += 1

            if generated % 1_000 == 0:
                await asyncio.sleep(0)

        return generated


async def run_firehose(
    file_path: str,
    order_count: int = 100_000,
    capacity: int = 100_000,
) -> float:
    buffer = MMapRingBuffer(
        file_path,
        capacity=capacity,
    )

    firehose = MarketFirehose(buffer)

    start = time.perf_counter()

    generated = await firehose.generate_orders(order_count)

    elapsed = time.perf_counter() - start

    buffer.close()

    orders_per_second = generated / elapsed

    print(f"Orders generated : {generated:,}")
    print(f"Elapsed time     : {elapsed:.6f} seconds")
    print(f"Orders/second    : {orders_per_second:,.2f}")

    return orders_per_second


if __name__ == "__main__":
    asyncio.run(
        run_firehose(
            "market_orders.mmap",
            order_count=100_000,
            capacity=100_000,
        )
    )