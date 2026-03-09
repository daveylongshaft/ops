# Task: Merge User Mode Tests (5 -> 1)

## Goal

Merge these 5 files into one `tests/test_user_modes.py`:
- test_user_mode_away.py
- test_user_mode_invisible.py
- test_user_mode_operator.py
- test_user_mode_server_notices.py
- test_user_mode_wallops.py

## Why

All 5 files have identical helpers: send_irc(), recv_all_irc(), create_client(). Same setup, same assertion patterns.

## Rules
- Same tests, zero behavior change
- One shared set of helpers at top
- All 21 tests grouped by mode letter
- Delete the 5 old files after verifying merged file passes
- Verify: `python3 -m pytest tests/test_user_modes.py -v 2>&1 | tee tests/logs/test_user_modes.log | grep FAILED`
- Delete old log files for removed test files

Verified complete.
