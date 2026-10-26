# ChronosMatch

**A High-Performance Order Matching and Market Simulation Engine**

ChronosMatch is a portfolio project exploring low-latency trading systems using Python, Cython, AsyncIO, memory-mapped inter-process communication (IPC), and SQLite.

The project implements a limit order matching engine, a shared-memory ring buffer, a synthetic market order generator, trade persistence, performance measurements, and a terminal-based latency dashboard.

## Features

- **Order Matching Engine:** Processes buy and sell orders using price-time priority, with support for partial fills and multiple price levels.
- **Cython Optimization:** Provides an optimized matching implementation and benchmarks it against the Python implementation.
- **Memory-Mapped IPC:** Uses a ring buffer to transfer order data between separate processes.
- **Async Market Firehose:** Generates synthetic orders and measures order-generation throughput.
- **Latency Monitoring:** Records order-submission latency and reports average and maximum latency in the demo dashboard.
- **Whale Sweep Detection:** Identifies orders that execute across multiple price levels.
- **Trade Persistence:** Stores executed trades in SQLite and supports asynchronous batch flushing.
- **Automated Testing:** Includes tests for matching behavior, IPC, persistence, dashboard functionality, and other project components.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application and simulation |
| Cython | Optimized matching implementation |
| AsyncIO | Asynchronous order generation and trade flushing |
| Memory-mapped files | Shared-memory IPC |
| SQLite | Trade persistence |
| pytest | Automated testing |
| curses | Terminal-based monitoring dashboard |
| Git and GitHub | Version control |

## Project Structure

```text
ChronosMatch/
├── benchmarks/
│   ├── benchmark_cython.py
│   ├── benchmark_engine.py
│   ├── benchmark_ipc.py
│   ├── benchmark_matching.py
│   └── profile_engine.py
├── docs/
├── data/
├── src/
│   └── chronosmatch/
│       ├── dashboard/
│       │   └── latency_dashboard.py
│       ├── ipc/
│       │   ├── ring_buffer.py
│       │   └── trade_ring_buffer.py
│       ├── matching/
│       │   ├── engine.py
│       │   ├── order.py
│       │   ├── order_book.py
│       │   ├── cython_adapter.py
│       │   └── cython/
│       │       └── match_core.pyx
│       ├── monitoring/
│       ├── simulation/
│       │   └── market_firehose.py
│       └── storage/
│           ├── async_trade_flusher.py
│           └── trade_ledger.py
├── tests/
├── pyproject.toml
├── setup.py
├── WEEK2_RESULTS.md
├── WEEK3_BASELINE.md
├── WEEK3_OPTIMIZATION_RESULTS.md
└── README.md
```

## Requirements

- Python 3.12 or later
- Cython 3.3 or later
- A C compiler compatible with the installed Python environment for building the Cython extension
- pytest for running the test suite

The project was tested in a Windows environment with Python 3.14.3.

## Installation

Open a terminal in the project directory.

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Install the project

```bash
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pytest
```

The editable installation builds the project according to its packaging configuration. If the Cython extension has not been built successfully, check the build output and the compiler requirements before running the optimized engine.

## Run the Dashboard

Launch the terminal dashboard from the project root:

```bash
python -m chronosmatch.dashboard.latency_dashboard
```

The dashboard displays:

- AAPL bid and ask prices
- Order book quantities
- Spread and mid-price when both sides are available
- Number of submitted orders and executed trades
- Average and maximum order-submission latency
- Multi-level whale sweep alerts

Press **Q** to exit.

The current dashboard uses a predefined in-memory demonstration workload. It is not, by itself, a live visualization of the complete IPC and SQLite pipeline.

## Run the Tests

```bash
pytest -q
```

Latest verified result:

```text
81 passed in 0.48s
```

## Run the Benchmarks

Run commands from the project root.

### 1. Two-Process IPC Benchmark

```bash
python benchmarks/benchmark_ipc.py
```

Latest verified result:

| Metric | Result |
|---|---:|
| Orders transferred | 1,000,000 |
| Ring buffer capacity | 65,536 |
| Elapsed time | 2.420883 seconds |
| Throughput | 413,072 orders/second |
| Producer exit code | 0 |
| Consumer exit code | 0 |
| Result | PASS |

This benchmark measures order transfer between two processes. It does not measure the complete trading pipeline's end-to-end throughput.

### 2. Market Firehose Benchmark

```bash
python -m chronosmatch.simulation.market_firehose
```

Latest verified result:

| Metric | Result |
|---|---:|
| Orders generated | 100,000 |
| Elapsed time | 0.114061 seconds |
| Throughput | 876,722.32 orders/second |

This measures synthetic order generation and memory-mapped buffer writes in the firehose benchmark. It should not be interpreted as end-to-end matching throughput.

### 3. Python vs. Cython Matching Benchmark

```bash
python benchmarks/benchmark_matching.py
```

Previously verified results from five measured rounds:

| Metric | Python | Cython |
|---|---:|---:|
| Median throughput | 687,786 orders/sec | 1,261,933 orders/sec |
| Average latency | 1.238 µs | 0.604 µs |
| P50 latency | 0.700 µs | 0.300 µs |
| P95 latency | 2.900 µs | 1.400 µs |
| P99 latency | 3.000 µs | 2.400 µs |

**Measured median throughput speedup: 1.83×.**

All five measured rounds passed the benchmark's matching-equivalence checks. These are synthetic, workload-specific results, not guarantees of production trading performance.

## Example Dashboard Behavior

The verified demonstration submitted six orders and executed three trades.

The final buy order swept three resting ask price levels:

- $150.00
- $151.00
- $152.00

The dashboard reported 150 executed shares across those levels, with an average measured submission latency of 5,567 ns and a maximum of 13,100 ns for that demonstration run.

These latency figures are specific to the small demo workload and should not be compared directly with the separate matching benchmark.

## Engineering Notes

ChronosMatch explores several concepts used in performance-sensitive systems:

1. Maintaining an order book and executing trades according to price-time priority.
2. Reducing matching overhead with a Cython implementation.
3. Transferring order data across processes using a memory-mapped ring buffer.
4. Measuring throughput and latency under synthetic workloads.
5. Detecting orders that execute across multiple price levels.
6. Persisting trade records asynchronously using SQLite.

The IPC, firehose, and matching benchmarks exercise different parts of the system. A combined end-to-end benchmark connecting order generation, IPC consumption, matching, trade persistence, and monitoring remains a separate integration-validation task.

## Future Improvements

- Add a reproducible end-to-end benchmark covering the complete order-to-trade path.
- Measure latency percentiles under sustained load.
- Validate backpressure and buffer-full behavior under consumer slowdown.
- Improve benchmark repeatability and document hardware and environment details.
- Expand the dashboard to consume live system metrics rather than only a predefined demonstration workload.

## Disclaimer

ChronosMatch is an educational and portfolio project for exploring order matching, IPC, performance optimization, and market simulation. Its synthetic benchmarks do not establish production readiness, exchange compliance, or suitability for real-money trading.

## Author

**Shivanandini Saddanapu**

GitHub: [ShivanandiniSaddanapu](https://github.com/ShivanandiniSaddanapu)
