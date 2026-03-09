# Task: Fix Failing Test — live_botserv_real_client_test

## What Failed

Test file: `tests/live_botserv_real_client_test.py`
Log file: `tests/logs/live_botserv_real_client_test.log`

### FAILED lines

```
tests/live_botserv_real_client_test.py::TestLiveBotservRealClient::test_botserv_filter_management_live FAILED [ 50%]
FAILED tests/live_botserv_real_client_test.py::TestLiveBotservRealClient::test_botserv_filter_management_live
```

## Instructions

1. Read the full log at `tests/logs/live_botserv_real_client_test.log`
2. Identify root cause of each failure
3. Fix the **code under test**, not the test (unless the test itself is wrong)
4. `rm tests/logs/live_botserv_real_client_test.log` (so cron re-runs the test)
5. Commit, push, move this prompt to done. **Do NOT run pytest yourself.**
