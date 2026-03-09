# Task: Fix Failing Test — botserv_logs

## What Failed

Test file: `tests/test_botserv_logs.py`
Log file: `tests/logs/test_botserv_logs.log`

### FAILED lines

```
tests/test_botserv_logs.py::TestBotServLogs::test_setlog_command FAILED  [100%]
FAILED tests/test_botserv_logs.py::TestBotServLogs::test_setlog_command - Att...
```

## Instructions

1. Read the full log at `tests/logs/test_botserv_logs.log`
2. Identify root cause of each failure
3. Fix the **code under test**, not the test (unless the test itself is wrong)
4. `rm tests/logs/test_botserv_logs.log` (so cron re-runs the test)
5. Commit, push, move this prompt to done. **Do NOT run pytest yourself.**
