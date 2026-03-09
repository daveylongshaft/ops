# Task: Merge NickServ Tests (3 -> 1)

## Goal

Merge these 3 files into one `tests/test_nickserv.py`:
- test_nickserv_ghost.py
- test_nickserv_registration.py
- test_stale_nick_cleanup.py

## Why

All 3 share identical _build_mock_server() and _register_client() helpers.

## Rules
- Same tests, zero behavior change
- One shared _build_mock_server() and _register_client() at top
- Tests grouped by feature (registration, ghost, stale cleanup)
- Delete the 3 old files after verifying
- Verify: `python3 -m pytest tests/test_nickserv.py -v 2>&1 | tee tests/logs/test_nickserv.log | grep FAILED`

Verified complete.
