# Task: Fix NickServ Mock Crash in Persistence Tests

## What Failed

14 tests in `TestHandlerPersistence` all crash during registration with:
```
TypeError: float() argument must be a string or a real number, not 'Mock'
```

At `server_message_handler.py:490`:
```python
enforce_timer = threading.Timer(float(timeout), self._nickserv_enforce, args=(addr, nick))
```

## Root Cause

The test's mock `storage.load_settings()` returns `{"nickserv": {"enforce_timeout": 60, "enforce_mode": "disconnect"}}` — but `storage.nickserv_get()` returns `Mock()` (truthy), which triggers NickServ enforcement. Inside the enforcement path, `settings.get("enforce_timeout", 60)` works, but `float(timeout)` fails because `timeout` ends up as a Mock somewhere in the chain.

The fix is in the **test mock setup** — `storage.nickserv_get` should return `None` (no registered nick) so NickServ enforcement is never triggered during test registration. Alternatively, the load_settings mock return value may need the correct nested structure.

## Files

- `tests/test_persistence.py` — `_build_mock_server()` or `TestHandlerPersistence.setUp()` mock setup
- `packages/csc-server/server_message_handler.py:490` — the crashing line (for reference only)

## Instructions

1. Read `tests/test_persistence.py` — find `_build_mock_server` or equivalent setUp that creates the mock
2. Ensure `storage.nickserv_get` returns `None` so NickServ enforcement is skipped during registration
3. Alternatively ensure `storage.load_settings` returns a properly structured dict where `enforce_timeout` is a real number (60)
4. Verify this fixes all 14 `TestHandlerPersistence` tests
5. `rm tests/logs/test_persistence.log`
6. Commit, push, move to done. Do NOT run tests.
--- AGENT gemini-3-pro Tue 17 Feb 2026 10:07:22 AM GMT ---
Starting task: Fix NickServ Mock Crash in Persistence Tests
Updating _build_mock_server in tests/test_persistence.py to set server.storage.nickserv_get.return_value = None. This prevents the NickServ enforcement logic from triggering during tests, avoiding the crash where a Mock object is passed to float().
Deleting stale log file tests/logs/test_persistence.log
Committing fix and pushing to main

PID: 5788 agent: gemini-3-pro starting at 2026-02-26 15:14:40


--- Agent Log ---
ERROR: Workorder not found: C:\csc\agents\gemini-3-pro\queue\work\orders.md


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)


--- Agent Log ---
ERROR: Workorder not found: C:\csc\agents\gemini-3-pro\queue\work\orders.md


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)


--- Agent Log ---
ERROR: Workorder not found: C:\csc\agents\gemini-3-pro\queue\work\orders.md


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)
