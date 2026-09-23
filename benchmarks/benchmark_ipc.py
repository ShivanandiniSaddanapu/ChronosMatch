import multiprocessing as mp
import os
import tempfile
import time

from chronosmatch.ipc.ring_buffer import MMapRingBuffer


NUMBER_OF_ORDERS = 1_000_000
CAPACITY = 65_536


def producer(file_path: str):
    buffer = MMapRingBuffer(file_path, CAPACITY)

    for order_id in range(NUMBER_OF_ORDERS):
        while buffer.is_full:
            time.sleep(0)

        buffer.write(
            order_id,
            100.0,
            10,
        )

    buffer.close()


def consumer(file_path: str, result_queue):
    buffer = MMapRingBuffer(file_path, CAPACITY)

    received = 0

    while received < NUMBER_OF_ORDERS:
        order = buffer.read()

        if order is None:
            time.sleep(0)
            continue

        order_id, price, quantity = order

        if order_id != received:
            result_queue.put(
                f"Order mismatch: expected {received}, got {order_id}"
            )
            buffer.close()
            return

        if price != 100.0 or quantity != 10:
            result_queue.put(
                f"Invalid order data: {order}"
            )
            buffer.close()
            return

        received += 1

    buffer.close()
    result_queue.put(received)


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(
            temp_dir,
            "orders.mmap",
        )

        # Initialize the shared mmap file before
        # starting the producer and consumer.
        buffer = MMapRingBuffer(
            file_path,
            CAPACITY,
        )
        buffer.close()

        result_queue = mp.Queue()

        producer_process = mp.Process(
            target=producer,
            args=(file_path,),
        )

        consumer_process = mp.Process(
            target=consumer,
            args=(
                file_path,
                result_queue,
            ),
        )

        start = time.perf_counter()

        producer_process.start()
        consumer_process.start()

        producer_process.join()
        consumer_process.join()

        elapsed = time.perf_counter() - start

        result = result_queue.get()

        print("=== Two-Process IPC Audit ===")
        print(f"Orders transferred : {NUMBER_OF_ORDERS:,}")
        print(f"Capacity           : {CAPACITY:,}")
        print(f"Elapsed time       : {elapsed:.6f} seconds")

        if isinstance(result, int):
            throughput = NUMBER_OF_ORDERS / elapsed

            print(f"Orders/second      : {throughput:,.0f}")
            print(f"Producer exit code : {producer_process.exitcode}")
            print(f"Consumer exit code : {consumer_process.exitcode}")
            print("Result             : PASS")
        else:
            print(f"Result             : FAIL")
            print(result)


if __name__ == "__main__":
    mp.freeze_support()
    main()