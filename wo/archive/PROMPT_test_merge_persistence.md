# Task: Merge Persistence Tests (3 -> 1)

## Goal

Merge these 3 files into one `tests/test_persistence.py`:
- test_complete_persistence.py
- test_handler_persistence.py
- test_power_failure_resilience.py

## Why

All 3 share _build_mock_server(storage_dir) with real PersistentStorageManager + ChannelManager.

## Rules
- Same tests, zero behavior change
- One shared mock server builder at top
- Tests grouped: complete, handler, power failure
- Delete the 3 old files after verifying
- Verify: `python3 -m pytest tests/test_persistence.py -v 2>&1 | tee tests/logs/test_persistence.log | grep FAILED`

Verified complete.
