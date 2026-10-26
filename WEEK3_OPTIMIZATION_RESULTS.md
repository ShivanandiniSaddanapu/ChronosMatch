# Week 3: Cython Matching Optimization Results

## Optimization
- Added a CTrade C structure for storing trade results.
- Added a preallocated C-level trade buffer.
- Stored trade results in C memory during the matching loop.
- Converted buffered trades into Python tuples after matching completed.
- Preserved the existing adapter return format.

## Correctness Verification
- Test command: pytest -q --basetemp=.pytest-tmp
- Result: 37 passed

## Direct Cython Benchmark
- Orders per run: 50,000
- Runs: 5
- Previous average time: 0.009992 seconds
- New average time: 0.008991 seconds
- Previous throughput: 5,003,893 orders/second
- New throughput: 5,561,179 orders/second
- Throughput improvement: approximately 11.1%

## Engine Comparison
- Python engine: 440,836 orders/second
- Cython adapter: 601,986 orders/second
- Measured adapter speedup: 1.37x

## Observation
Direct Cython throughput improved in this measurement, but adapter throughput
was lower than the previous baseline. Further benchmarking is needed before
claiming an overall performance improvement.

## Limitations
The matching loop stores trade records in C memory, but the method still
creates Python tuples and a list when returning results.



# Week 3: Cython Matching Optimization Results

## Optimization Implemented

- Added a `CTrade` C structure for storing trade results.
- Added a preallocated C-level trade buffer.
- Stored trade results in C memory during the matching loop.
- Converted buffered trades into Python tuples after matching completed.
- Preserved the existing adapter return format.
- Updated both benchmark scripts to use `time.perf_counter_ns()` for elapsed-time measurements.

## Correctness Verification

- Test command: `pytest -q --basetemp=.pytest-tmp`
- Latest result: **37 passed**
- Fresh Cython extension import: verified successfully.

## Latest Direct Cython Benchmark

| Metric | Result |
|---|---:|
| Orders per run | 50,000 |
| Runs | 5 |
| Average elapsed time | 10.13456 ms |
| Average throughput | 4,933,613 orders/second |

### Historical Direct Cython Measurement

The earlier report recorded a throughput of 5,003,893 orders/second. The latest result is slightly lower, so the current measurements do not establish a direct-Cython performance improvement.

An earlier measurement of 5,561,179 orders/second was also recorded. These measurements vary, and the original baseline should not be treated as a guaranteed performance level.

## Latest Engine Comparison

| Metric | Python MatchingEngine | Cython Matching Adapter |
|---|---:|---:|
| Runs | 5 | 5 |
| Orders per run | 50,000 | 50,000 |
| Average elapsed time | 110.5704 ms | 86.46324 ms |
| Average throughput | 452,201 orders/second | 578,280 orders/second |

Measured adapter speedup: **1.28×**.

The adapter delivered approximately 27.9% higher throughput than the Python engine in this benchmark run.

## Historical Three-Run Adapter Comparison

| Run | Python orders/sec | Adapter orders/sec | Speedup |
|---|---:|---:|---:|
| 1 | 449,709 | 637,508 | 1.42× |
| 2 | 439,067 | 597,446 | 1.36× |
| 3 | 450,878 | 634,367 | 1.41× |

Average speedup across these historical runs: approximately 1.40×.

An earlier separate measurement recorded 440,836 orders/second for the Python engine and 601,986 orders/second for the adapter, a speedup of 1.37×.

Historical measurements are retained for comparison and are not combined with the latest five-run benchmark.

## Interpretation and Limitations

- The latest engine benchmark shows that the Cython adapter outperformed the Python engine for the tested workload.
- The measured speedup varies between runs.
- The latest direct Cython throughput is slightly below the earlier 5,003,893 orders/second baseline.
- The matching loop stores trade records in C memory, but the method still creates Python tuples and a list when returning results.
- Benchmark results depend on the environment, workload, and measurement conditions. Further repeated measurements are needed before making broader performance claims.

## Week 3 Verification Checklist

- [x] Fresh Cython extension import verified.
- [x] Automated tests passed: 37/37.
- [x] Nanosecond timing added to both benchmark scripts.
- [x] Direct Cython benchmark executed.
- [x] Python versus Cython adapter benchmark executed.
- [x] Temporary test directory removed.
- [x] Git whitespace check completed without whitespace errors.
- [ ] Final report and changes committed.

Week 3 is pending the final Git review and commit.
