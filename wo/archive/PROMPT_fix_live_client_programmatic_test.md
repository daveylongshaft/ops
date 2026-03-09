# Task: Fix Failing Test — live_client_programmatic_test

## What Failed

Test file: `tests/live_client_programmatic_test.py`
Log file: `tests/logs/live_client_programmatic_test.log`

### FAILED lines

```
tests/live_client_programmatic_test.py::TestLiveClientProgrammatic::test_client_detach_only FAILED [ 50%]
tests/live_client_programmatic_test.py::TestLiveClientProgrammatic::test_client_programmatic_mode FAILED [100%]
FAILED tests/live_client_programmatic_test.py::TestLiveClientProgrammatic::test_client_detach_only
FAILED tests/live_client_programmatic_test.py::TestLiveClientProgrammatic::test_client_programmatic_mode
```

## Instructions

1. Read the full log at `tests/logs/live_client_programmatic_test.log`
2. Identify root cause of each failure
3. Fix the **code under test**, not the test (unless the test itself is wrong)
4. `rm tests/logs/live_client_programmatic_test.log` (so cron re-runs the test)
5. Commit, push, move this prompt to done. **Do NOT run pytest yourself.**
