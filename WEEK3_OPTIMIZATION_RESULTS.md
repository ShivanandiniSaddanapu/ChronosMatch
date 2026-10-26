# ChronosMatch — Week 3 Cython Matching Optimization Results

## 1. Objectives

The objectives for Week 3 were to:

- Reduce Python-object interaction in the Cython matching hot path.
- Preserve matching correctness and price-time priority.
- Measure execution time, throughput, and order-submission latency.
- Run regression tests and compare the Python engine with the Cython adapter.

## 2. Optimization Implemented

The following changes were implemented:

- Added a `CTrade` C structure to store trade results.
- Added a preallocated C-level trade buffer.
- Stored trade results in C memory during the matching loop.
- Converted buffered trade results into Python tuples after matching.
- Preserved the existing adapter return format.
- Added validation to reject non-finite, zero, and negative prices.
- Added automated tests for invalid prices and order-book capacity.
- Used `time.perf_counter_ns()` for nanosecond-resolution timing measurements.

## 3. Correctness Verification

The Cython extension was rebuilt successfully using:

```powershell
python setup.py build_ext --inplace --force
```

The complete test suite was executed using:

```powershell
pytest -q --basetemp=.pytest-tmp
```

**Latest result: 48 passed in 2.80 seconds.**

The successful test run verifies the covered matching, adapter, order-book, simulation, IPC, and validation behaviors.

## 4. Latest Python Engine vs. Cython Adapter Benchmark

### Configuration

- Orders per run: 50,000
- Number of runs: 5
- Workload: Alternating BUY and SELL orders
- Price: 100.0
- Quantity per order: 10
- Timing: `time.perf_counter_ns()`

### Results

| Metric | Python MatchingEngine | Cython Matching Adapter |
|---|---:|---:|
| Average workload time | 98.06336 ms | 76.16506 ms |
| Average workload time | 98,063,360 ns | 76,165,060 ns |
| Average order-submission latency | 998 ns | 591 ns |
| Minimum observed order latency | 600 ns | 300 ns |
| Maximum observed order latency | 183,700 ns | 926,800 ns |
| Throughput | 509,874 orders/second | 656,469 orders/second |

### Performance Comparison

The Cython adapter achieved approximately **1.29× throughput**, or **28.8% higher throughput**, than the Python matching engine in this benchmark run.

The average measured order-submission latency was lower for the Cython adapter. However, the adapter's maximum observed latency was higher, demonstrating that average performance does not represent every individual order.

These figures describe the latest measured run and are not universal performance guarantees.

## 5. Latest Direct Cython Benchmark

### Configuration

- Orders per run: 50,000
- Number of runs: 5
- Timing: `time.perf_counter_ns()`

### Results

| Metric | Result |
|---|---:|
| Average runtime | 0.00695748 seconds |
| Average runtime | 6,957,480 nanoseconds |
| Throughput | 7,186,510 orders/second |

This benchmark measures the direct Cython matching path. Its results should not be compared directly with the Python engine or adapter benchmark because the execution paths and measurement scope differ.

Earlier direct-Cython measurements varied. The latest result is recorded as a separate measurement rather than combined with historical results.

## 6. Interpretation and Limitations

- The latest engine comparison showed higher throughput for the Cython adapter than for the Python engine under the tested workload.
- Benchmark results depend on the environment, workload, and measurement overhead.
- `time.perf_counter_ns()` provides nanosecond-resolution readings; it does not guarantee nanosecond measurement accuracy.
- Order-submission latency measures the duration of `engine.submit(order)`. It is not end-to-end IPC latency or individual trade-fill latency.
- The Cython matching method still creates Python tuples and a list when returning trade results.
- The direct Cython benchmark and adapter benchmark use different execution paths and should be interpreted separately.
- These measurements do not prove that every order completes within 50 microseconds or guarantee production performance.
- Further profiling and repeated measurements may be useful before making broader performance claims.

## 7. Week 3 Verification Checklist

- [x] C-level trade structure implemented.
- [x] Preallocated C-level trade buffer implemented.
- [x] Existing adapter return format preserved.
- [x] Invalid-price validation implemented.
- [x] Automated validation and regression tests executed.
- [x] Cython extension rebuilt successfully.
- [x] Full test suite passed: 48/48.
- [x] Python engine versus Cython adapter benchmark executed.
- [x] Direct Cython benchmark executed.
- [x] Temporary pytest directory removed.
- [ ] Final Git review completed.
- [ ] Final changes committed and pushed to GitHub.

## 8. Week 3 Status

The Cython optimization, validation changes, regression testing, and benchmark execution are complete.

The remaining steps are to review the final Git diff, verify that generated files and temporary artifacts are handled correctly, commit the intended changes, and push them to GitHub.

**Week 3 should be marked fully complete after the final review and successful push.**
