# Task: Fix Failing Test — 0000_verify_client_bridge_localserver_service_commands

## What Failed

Test file: `tests/test_0000_verify_client_bridge_localserver_service_commands.py`
Log file: `tests/logs/test_0000_verify_client_bridge_localserver_service_commands.log`

### FAILED lines

```
tests/test_0000_verify_client_bridge_localserver_service_commands.py::test_0000_verify_client_bridge_localserver_service_commands FAILED [100%]
✗ CRITICAL TESTS FAILED - See diagnostic output above
FAILED tests/test_0000_verify_client_bridge_localserver_service_commands.py::test_0000_verify_client_bridge_localserver_service_commands
```

## Instructions

1. Read the full log at `tests/logs/test_0000_verify_client_bridge_localserver_service_commands.log`
2. Identify root cause of each failure
3. Fix the **code under test**, not the test (unless the test itself is wrong)
4. `rm tests/logs/test_0000_verify_client_bridge_localserver_service_commands.log` (so cron re-runs the test)
5. Commit, push, move this prompt to done. **Do NOT run pytest yourself.**
