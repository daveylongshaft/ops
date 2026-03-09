# Task: Fix Failing Test — storage_manager

## What Failed

Test file: `tests/test_storage_manager.py`
Log file: `tests/logs/test_storage_manager.log`

### FAILED lines

```
tests/test_storage_manager.py::TestChannelOperations::test_save_and_load_channels FAILED [ 53%]
tests/test_storage_manager.py::TestChannelOperations::test_save_channels_from_manager FAILED [ 60%]
FAILED tests/test_storage_manager.py::TestChannelOperations::test_save_and_load_channels
FAILED tests/test_storage_manager.py::TestChannelOperations::test_save_channels_from_manager
```

## Instructions

1. Read the full log at `tests/logs/test_storage_manager.log`
2. Identify root cause of each failure
3. Fix the **code under test**, not the test (unless the test itself is wrong)
4. `rm tests/logs/test_storage_manager.log` (so cron re-runs the test)
5. Commit, push, move this prompt to done. **Do NOT run pytest yourself.**
--- RESTART Tue 17 Feb 2026 02:13:02 PM GMT ---
AGENT_PID: 218563
read tests/logs/test_storage_manager.log — identifying failure root cause
add PersistentStorageManager.load_channels() — public alias for _load_channels_from_disk to fix tests
replace get_latest_channels_data with load_channels in packages/csc-server/storage.py
remove tests/logs/test_storage_manager.log
--- RESTART Tue 17 Feb 2026 02:24:22 PM GMT ---
AGENT_PID: 249780
Resuming orphaned task to fix storage_manager tests
