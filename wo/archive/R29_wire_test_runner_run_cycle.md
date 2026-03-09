> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# R29: Wire test-runner run_cycle() Into Main Loop

## Depends: R10, R14

## Task
Add a `run_cycle()` function to `packages/csc-service/csc_service/infra/test_runner.py`
and wire it into the main loop.

## Steps

1. Open `packages/csc-service/csc_service/infra/test_runner.py`

2. Find the main entry point or the function that runs one test cycle.
   The existing test-runner likely has `if __name__ == "__main__":` at the bottom.

3. Add a `run_cycle()` function that does one pass (scan for missing logs, run tests, generate fix prompts). If the existing code already has this as a function, just expose it. If it's all in `main()`, extract the single-cycle logic into `run_cycle(work_dir=None)`.

4. The function signature should be:
```python
def run_cycle(work_dir=None):
    """Run one test cycle. Returns number of tests run."""
    # ... existing single-cycle logic ...
```

5. Open `packages/csc-service/csc_service/main.py` and replace the `pass` placeholder under `enable_test_runner` with:
```python
from csc_service.infra import test_runner
count = test_runner.run_cycle(work_dir=work_dir)
if count:
    print(f"[{ts()}] [test-runner] Ran {count} test(s)")
```

## Verification
- `grep "def run_cycle" packages/csc-service/csc_service/infra/test_runner.py` finds the function
- `grep "test_runner.run_cycle" packages/csc-service/csc_service/main.py` finds the call
