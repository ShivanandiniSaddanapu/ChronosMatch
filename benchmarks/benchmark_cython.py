import time

from chronosmatch.matching.cython.match_core import CythonOrderBook


NUMBER_OF_ORDERS = 50_000
RUNS = 5


def workload(number_of_orders: int = NUMBER_OF_ORDERS) -> None:
    book = CythonOrderBook(number_of_orders + 1)

    for order_id in range(number_of_orders):
        if order_id % 2 == 0:
            book.match_order(
                order_id,
                100.0,
                10,
                1,
            )
        else:
            book.match_order(
                order_id,
                100.0,
                10,
                0,
            )


def benchmark(runs: int = RUNS):
    results = []

    for _ in range(runs):
        start = time.perf_counter()
        workload()
        elapsed = time.perf_counter() - start
        results.append(elapsed)

    average_time = sum(results) / len(results)
    throughput = NUMBER_OF_ORDERS / average_time

    print("=== Direct Cython Matching ===")
    print(f"Runs            : {runs}")
    print(f"Orders per run  : {NUMBER_OF_ORDERS:,}")
    print(f"Average time    : {average_time:.6f} seconds")
    print(f"Throughput      : {throughput:,.0f} orders/second")


if __name__ == "__main__":
    benchmark()
