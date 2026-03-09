# Task: Fix Failing Test — agent_separate_repo

## What Failed

Test file: `tests/test_agent_separate_repo.py`
Log file: `tests/logs/test_agent_separate_repo.log`

### FAILED lines

```
tests/test_agent_separate_repo.py::TestPlatformTempRoot::test_platform_json_stores_temp_root FAILED [ 11%]
tests/test_agent_separate_repo.py::TestPlatformTempRoot::test_platform_properties_work FAILED [ 22%]
FAILED tests/test_agent_separate_repo.py::TestPlatformTempRoot::test_platform_json_stores_temp_root
FAILED tests/test_agent_separate_repo.py::TestPlatformTempRoot::test_platform_properties_work
```

## Instructions

1. Read the full log at `tests/logs/test_agent_separate_repo.log`
2. Identify root cause of each failure
3. Fix the **code under test**, not the test (unless the test itself is wrong)
4. `rm tests/logs/test_agent_separate_repo.log` (so cron re-runs the test)
5. Commit, push, move this prompt to done. **Do NOT run pytest yourself.**


--- Agent Log ---
Done. The fix is a one-line addition in `packages/csc-service/csc_service/shared/platform.py`:

**Root cause:** `_detect_runtime()` computed `csc_agent_work = temp_root / "csc"` and stored the path string, but never created the directory. Tests asserted `.exists()` on this path, which failed.

**Fix:** Added `csc_agent_work.mkdir(parents=True, exist_ok=True)` before storing the path, ensuring the directory exists when Platform is instantiated.
[run_agent] Agent: opus, Root: C:\Users\davey\AppData\Local\Temp\csc\opus\repo
[run_agent] Starting Claude (claude-opus-4-6) for opus


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)


--- Agent Log ---
Done. The fix is a one-line addition in `packages/csc-service/csc_service/shared/platform.py`:

**Root cause:** `_detect_runtime()` computed `csc_agent_work = temp_root / "csc"` and stored the path string, but never created the directory. Tests asserted `.exists()` on this path, which failed.

**Fix:** Added `csc_agent_work.mkdir(parents=True, exist_ok=True)` before storing the path, ensuring the directory exists when Platform is instantiated.
[run_agent] Agent: opus, Root: C:\Users\davey\AppData\Local\Temp\csc\opus\repo
[run_agent] Starting Claude (claude-opus-4-6) for opus


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)


--- Agent Log ---
Done. The fix is a one-line addition in `packages/csc-service/csc_service/shared/platform.py`:

**Root cause:** `_detect_runtime()` computed `csc_agent_work = temp_root / "csc"` and stored the path string, but never created the directory. Tests asserted `.exists()` on this path, which failed.

**Fix:** Added `csc_agent_work.mkdir(parents=True, exist_ok=True)` before storing the path, ensuring the directory exists when Platform is instantiated.
[run_agent] Agent: opus, Root: C:\Users\davey\AppData\Local\Temp\csc\opus\repo
[run_agent] Starting Claude (claude-opus-4-6) for opus


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)
