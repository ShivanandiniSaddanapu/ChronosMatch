# ChronosMatch
High-Performance Order Matching and Market Simulation Engine built with Python, Cython, AsyncIO, IPC, and SQLite.


## Performance Baseline

Initial pure-Python benchmark on a Windows environment with Python 3.14.3:

| Workload | Orders | Throughput |
|----------|-------:|-----------:|
| Matching | 10,000 | 576,811 orders/sec |
| Order Book | 10,000 | 733,396 orders/sec |

These are preliminary synthetic benchmark results from a single run. Further benchmarking
will evaluate larger workloads, repeated runs, price levels, partial fills, and optimized
implementations.