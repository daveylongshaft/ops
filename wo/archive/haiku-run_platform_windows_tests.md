---
requires: [python3, git]
platform: [windows]
---
# Run Platform Detection Tests on Windows

## Recommended Agent: haiku (lightweight test validation)

## Goal
Verify that `tests/test_platform_windows.py` passes on a real Windows machine.

## Steps

1. `git pull` to get latest code
2. Verify you're on Windows: `python -c "import sys; print(sys.platform)"`
3. Delete the stale log if it exists: `rm tests/logs/test_platform_windows.log`
4. Let cron run the test, OR if no cron on this box: `python -m pytest tests/test_platform_windows.py -v`
5. If tests pass: commit the log, push
6. If tests fail: fix the platform detection code in `packages/csc_shared/platform.py`, commit, push

## What the tests verify
- `platform.system()` returns "Windows"
- RAM detection via ctypes GlobalMemoryStatus works
- Chocolatey package manager detection
- `matches_platform(["windows"])` returns True
- `matches_platform(["linux"])` returns False

## Files
- `tests/test_platform_windows.py` — the test file
- `tests/platform_gate.py` — platform gating helper
- `packages/csc_shared/platform.py` — the code under test
