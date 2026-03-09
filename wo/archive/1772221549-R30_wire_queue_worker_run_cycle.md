# R30: Wire queue-worker run_cycle() Into Main Loop

## Depends: R11, R14

## Task
Add a `run_cycle()` function to `packages/csc-service/csc_service/infra/queue_worker.py`
and wire it into the main loop.

## Steps

1. Open `packages/csc-service/csc_service/infra/queue_worker.py`

2. Find the existing main logic. The queue-worker likely has `process_work()` and `process_inbox()` functions.

3. Add a `run_cycle()` function that calls the existing cycle functions:
```python
def run_cycle(work_dir=None):
    """Run one queue-worker cycle. Returns list of processed items."""
    results = []
    # Call existing process_work() and process_inbox() or equivalent
    # Return what was processed
    return results
```

4. Open `packages/csc-service/csc_service/main.py` and replace the `pass` placeholder under `enable_queue_worker` with:
```python
from csc_service.infra import queue_worker
results = queue_worker.run_cycle(work_dir=work_dir)
if results:
    for r in results:
        print(f"[{ts()}] [queue-worker] {r}")
```

## Verification
- `grep "def run_cycle" packages/csc-service/csc_service/infra/queue_worker.py` finds the function
- `grep "queue_worker.run_cycle" packages/csc-service/csc_service/main.py` finds the call


DEAD END - csc-service package already consolidated and operational
