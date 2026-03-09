---
requires: [python3, git]
platform: [linux, windows, darwin]
---
# Design Cross-Platform CI Matrix for Platform Tests

## Recommended Agent: gemini-3.0-flash (fast reasoning, CI/CD design)

## Goal
Design a GitHub Actions workflow that runs the platform-specific tests on each target OS.

## Steps

1. Read the existing platform test files:
   - `tests/test_platform_windows.py`
   - `tests/test_platform_macos.py`
   - `tests/test_platform_docker.py`
   - `tests/test_platform_wsl.py`
   - `tests/test_platform.py` (generic, runs everywhere)

2. Create `.github/workflows/platform-tests.yml` with a matrix strategy:
   ```yaml
   strategy:
     matrix:
       os: [ubuntu-latest, windows-latest, macos-latest]
   ```

3. Each matrix entry should:
   - Install Python 3.10+
   - Install csc-shared package
   - Run only the platform-specific test for that OS
   - Upload test logs as artifacts

4. Add a Docker job that runs `test_platform_docker.py` inside a container

5. Commit the workflow, push, verify it runs on GitHub

## Files to create
- `.github/workflows/platform-tests.yml`

## Files to reference
- `tests/platform_gate.py` — the gating mechanism
- `tests/run_tests.sh` — local cron runner (already handles PLATFORM_SKIP)
