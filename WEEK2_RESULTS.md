# ChronosMatch — Week 2 Results

## Completed Work

### Cython Matching Engine
- Implemented a Cython-based order matching engine.
- Added C-level order structures using Cython types.
- Implemented Price-Time Priority matching.
- Verified BUY and SELL matching behavior with automated tests.

### Zero-Copy IPC
- Implemented shared read/write indexes inside the memory-mapped file header.
- Built a two-process Single Producer / Single Consumer (SPSC) data path.
- Orders are transferred through shared mmap storage without per-order serialization.

### IPC Audit
- Transferred 1,000,000 orders between two Python processes.
- Verified order IDs, prices, and quantities.
- Audit completed successfully with producer and consumer exit codes of 0.
- Benchmark result: approximately 588,420 orders/second in the recorded 1M-order run.

### Latency Dashboard
- Added a raw curses terminal dashboard.
- Displays:
  - Best Bid
  - Best Ask
  - Bid Quantity
  - Ask Quantity
  - Bid/Ask Spread
  - Mid Price
- Dashboard refreshes every 0.1 seconds.

## Verification

Full automated test suite:

- 37 tests passed
- Cython matching tests passed
- IPC tests passed
- Two-process mmap integration test passed
- Simulation tests passed

## Week 2 Status

Week 2 implementation, testing, IPC validation, and dashboard work are complete.