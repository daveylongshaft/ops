# Task: Fix Failing Test — remote_execution

## What Failed

Test file: `tests/test_remote_execution.py`
Log file: `tests/logs/test_remote_execution.log`

### FAILED lines

```
..\..\..\tests\test_remote_execution.py::TestRemoteExecution::test_remote_builtin_command FAILED [ 50%]
```

## Instructions

1. Read the full log at `tests/logs/test_remote_execution.log`
2. Identify root cause of each failure
3. Fix the **code under test**, not the test (unless the test itself is wrong)
4. `rm tests/logs/test_remote_execution.log` (so cron re-runs the test)
5. Commit, push, move this prompt to done. **Do NOT run pytest yourself.**
