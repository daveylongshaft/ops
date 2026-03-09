---
requires: [python3, git]
platform: [wsl]
---
# Run Platform Detection Tests Under WSL

## Recommended Agent: haiku (lightweight test validation)

## Goal
Verify that `tests/test_platform_wsl.py` passes under Windows Subsystem for Linux.

## Steps

1. `git pull` to get latest code
2. Verify you're on WSL: `uname -r` should contain "microsoft" or "WSL"
3. Delete the stale log if it exists: `rm tests/logs/test_platform_wsl.log`
4. Run: `python -m pytest tests/test_platform_wsl.py -v`
5. If tests pass: commit the log, push
6. If tests fail: fix the platform detection code, commit, push

## What the tests verify
- Virtualization type is "wsl"
- System reports as Linux
- Kernel release contains "microsoft"
- `matches_platform(["linux"])` returns True under WSL

## Files
- `tests/test_platform_wsl.py` — the test file
- `packages/csc_shared/platform.py` — the code under test
