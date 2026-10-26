# ChronosMatch — Week 3 Performance Baseline

## Objective
Record the existing matching-engine performance before Cython optimization.

## Benchmark Configuration
- Orders per run: 50,000
- Runs: 5
- Workload: Alternating BUY and SELL orders at price 100.0
- Quantity per order: 10
- Timing: time.perf_counter()

## Results

| Metric | Python Engine | Cython Adapter |
|---|---:|---:|
| Average runtime | 0.124732 s | 0.070023 s |
| Throughput | 400,860 orders/s | 714,049 orders/s |

Cython adapter speedup: 1.78x

### Direct Cython Benchmark

- Average runtime: 0.009992 seconds
- Throughput: 5,003,893 orders/second
- Orders per run: 50,000
- Runs: 5

## Python Profiler Observations

The 50,000-order Python workload reported approximately 550,004 function calls.

Functions with notable cumulative time:
- MatchingEngine.submit(): 0.210 s cumulative
- Order.create(): 0.105 s cumulative
- MatchingEngine._match_buy(): 0.090 s cumulative
- OrderBook.add(): 0.040 s cumulative

Profiler timing is instrumented and should not be compared directly with unprofiled benchmark timings.

## Interpretation

The direct Cython benchmark has the highest measured throughput in this workload.
The adapter benchmark includes Python-facing integration overhead.

These measurements are workload-specific. They do not establish end-to-end IPC latency or prove that every execution completes within 50 microseconds.

## Week 3 Optimization Goals

1. Reduce Python-object interaction in the Cython matching hot path.
2. Preserve matching correctness and price-time priority.
3. Record latency and throughput after optimization.
4. Run regression tests and compare results with this baseline.

## Verification Before Optimization

- Test suite: 37 passed
- Git working tree: clean before this report was added
