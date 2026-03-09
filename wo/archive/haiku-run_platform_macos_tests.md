---
requires: [python3, git]
platform: [darwin]
---
# Run Platform Detection Tests on macOS

## Recommended Agent: haiku (lightweight test validation)

## Goal
Verify that `tests/test_platform_macos.py` passes on a real Mac.

## Steps

1. `git pull` to get latest code
2. Verify you're on macOS: `python -c "import sys; print(sys.platform)"`
3. Delete the stale log if it exists: `rm tests/logs/test_platform_macos.log`
4. Let cron run the test, OR if no cron on this box: `python -m pytest tests/test_platform_macos.py -v`
5. If tests pass: commit the log, push
6. If tests fail: fix the platform detection code, commit, push

## What the tests verify
- `platform.system()` returns "Darwin"
- RAM detection via sysctl works
- Homebrew detection
- `matches_platform(["darwin"])` returns True
- `matches_platform(["windows"])` returns False

## Files
- `tests/test_platform_macos.py` — the test file
- `packages/csc_shared/platform.py` — the code under test
