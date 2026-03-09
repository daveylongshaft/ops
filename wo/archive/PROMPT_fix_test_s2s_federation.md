# Task: Fix Failing Test — s2s_federation

## What Failed

Test file: `tests/test_s2s_federation.py`
Log file: `tests/logs/test_s2s_federation.log`

### FAILED lines

```
tests/test_s2s_federation.py::test_s2s_sync_msg FAILED                   [ 66%]
tests/test_s2s_federation.py::test_s2s_sync_topic FAILED                 [100%]
FAILED tests/test_s2s_federation.py::test_s2s_sync_msg - assert False
FAILED tests/test_s2s_federation.py::test_s2s_sync_topic - assert False
```

## Instructions

1. Read the full log at `tests/logs/test_s2s_federation.log`
2. Identify root cause of each failure
3. Fix the **code under test**, not the test (unless the test itself is wrong)
4. `rm tests/logs/test_s2s_federation.log` (so cron re-runs the test)
5. Commit, push, move this prompt to done. **Do NOT run pytest yourself.**
