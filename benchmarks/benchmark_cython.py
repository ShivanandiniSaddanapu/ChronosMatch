
import time

from chronosmatch.matching.cython.match_core import CythonOrderBook


NUMBER_OF_ORDERS = 50_000
RUNS = 5
NANOSECONDS_PER_SECOND = 1_000_000_000


def workload(number_of_orders: int = NUMBER_OF_ORDERS) -> None:
    book = CythonOrderBook(number_of_orders + 1)

    for order_id in range(number_of_orders):
        if order_id % 2 == 0:
            book.match_order(order_id, 100.0, 10, 1)
        else:
            book.match_order(order_id, 100.0, 10, 0)


def benchmark(runs: int = RUNS):
    results_ns = []

    for _ in range(runs):
        start_ns = time.perf_counter_ns()
        workload()
        elapsed_ns = time.perf_counter_ns() - start_ns
        results_ns.append(elapsed_ns)

    average_ns = sum(results_ns) / len(results_ns)
    average_seconds = average_ns / NANOSECONDS_PER_SECOND
    throughput = NUMBER_OF_ORDERS / average_seconds

    print("=== Direct Cython Matching ===")
    print(f"Runs                 : {runs}")
    print(f"Orders per run       : {NUMBER_OF_ORDERS:,}")
    print(f"Average time         : {average_seconds:.6f} seconds")
    print(f"Average time         : {average_ns:,.0f} nanoseconds")
    print(f"Throughput           : {throughput:,.0f} orders/second")


if __name__ == "__main__":
    benchmark()
