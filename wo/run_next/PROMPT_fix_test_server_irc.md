# Task: Fix Failing Test — server_irc

## What Failed

Test file: `tests/test_server_irc.py`
Log file: `tests/logs/test_server_irc.log`

### FAILED lines

```
tests/test_server_irc.py::TestOper::test_oper_grants_kick_kill_privileges FAILED [ 57%]
tests/test_server_irc.py::TestOper::test_valid_oper_returns_381 FAILED   [ 59%]
FAILED tests/test_server_irc.py::TestOper::test_oper_grants_kick_kill_privileges
FAILED tests/test_server_irc.py::TestOper::test_valid_oper_returns_381 - Asse...
```

## Instructions

1. Read the full log at `tests/logs/test_server_irc.log`
2. Identify root cause of each failure
3. Fix the **code under test**, not the test (unless the test itself is wrong)
4. Re-run: `python3 -m pytest tests/test_server_irc.py -v > tests/logs/test_server_irc.log 2>&1`
5. Verify zero FAILED lines in the new log
--- RESTART Tue 17 Feb 2026 09:32:20 AM GMT ---
AGENT_PID: 205604
reading OPER handler in server_message_handler.py
root cause: mock storage.add_active_oper is no-op, opers set never populated
fix: add side_effect to mock add_active_oper to update opers set
all 52 tests pass — fix verified
moving to done and committing
