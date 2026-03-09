# Test Guidelines

## Never run tests. Never.

The test runner (`bin/test-runner`) polls every 60 seconds and runs tests automatically. Running tests yourself wastes API credits and is redundant.

## How the test cycle works

1. Test runner detects a missing log in `tests/logs/` → runs the test → writes the log
2. If test **passes**: log stays, test runner skips it next cycle
3. If test **fails**: test runner auto-generates `wo/ready/PROMPT_fix_test_<name>.md`
4. Next agent picks up the fix prompt and fixes the code

**Log file = lock.** If a log exists, the test runner won't rerun that test.

## Your job on a test-fix task

1. Read the failing log to understand what broke: `cat tests/logs/test_<name>.log | tail -20`
2. Find and fix the code
3. Delete the log to trigger retest: `rm tests/logs/test_<name>.log`
4. That's it. Do NOT run pytest. The test runner handles it.

## Writing new tests

Write tests if the task asks. Follow existing patterns in `tests/test_*.py`. Use pytest. Don't run them — just write and commit. The test runner picks them up within 1 minute.

## Platform-gated tests

Tests targeting a specific OS use `tests/platform_gate.py`:
```python
from platform_gate import require_platform
require_platform(["windows"])  # Skips with PLATFORM_SKIP on non-Windows
```

When a test prints `PLATFORM_SKIP:`, the log stays and locks that machine. Test runner generates a routing prompt to run the test on the right platform. Don't delete those logs — they're intentional.
