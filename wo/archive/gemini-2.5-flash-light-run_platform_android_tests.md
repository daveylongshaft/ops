---
requires: [python3, git]
platform: [android, termux]
---
# Run Platform Detection Tests on Android/Termux

## Recommended Agent: gemini-2.5-flash-light (practically free, simple validation)

## Goal
Verify that `tests/test_platform_android.py` passes on a real Android device running Termux.

## Steps

1. `git pull` to get latest code
2. Verify you're on Termux: `echo $TERMUX_VERSION`
3. Delete the stale log if it exists: `rm tests/logs/test_platform_android.log`
4. Run: `python -m pytest tests/test_platform_android.py -v`
5. If tests pass: commit the log, push
6. If tests fail: fix the platform detection code, commit, push

## What the tests verify
- `is_android` flag is True
- Distribution is "android-termux"
- Termux pkg package manager detection
- `matches_platform(["android"])` returns True
- Resource assessment works on mobile hardware

## Files
- `tests/test_platform_android.py` — the test file
- `packages/csc_shared/platform.py` — the code under test
