# Task: Create Windows Test Runner Using a Polling Service

## Goal

Create `tests/run_tests.ps1` (PowerShell) — a Windows equivalent of `tests/run_tests.sh` that produces identical log files and prompt files.
Instead of Task Scheduler, implement a script that runs as a Windows Service, polls the relevant directories every minute, and executes `run_tests.ps1` without creating pop-up windows. This service should stay running in the background.

## What the Linux Version Does

`tests/run_tests.sh` runs every minute via cron and does the following:

1. Scans `tests/test_*.py` and `tests/live_*.py` for test files
2. Skips any test that already has a log file in `tests/logs/` (log exists = already tested)
3. Runs each unlogged test via `python3 -m pytest <file> -v`, captures output to `tests/logs/<basename>.log`
4. Checks the log for `PLATFORM_SKIP:` lines — if found, the log **stays** (locks this machine), and a routing prompt is generated from `tests/platform_skip_template.md` into `prompts/ready/PROMPT_run_<basename>.md`
5. Checks the log for `FAILED` lines — if found, a fix prompt is generated from `tests/prompt_template.md` into `prompts/ready/PROMPT_fix_<basename>.md`
6. Never overwrites an existing prompt file
7. Idempotent — safe to run repeatedly

Key files:
- `tests/run_tests.sh` — the Linux script (reference implementation)
- `tests/prompt_template.md` — template for failed test prompts, uses `{{TEST_NAME}}`, `{{TEST_FILE}}`, `{{LOG_FILE}}`, `{{FAILED_LINES}}`
- `tests/platform_skip_template.md` — template for platform-skip prompts, uses `{{TEST_NAME}}`, `{{TEST_FILE}}`, `{{LOG_FILE}}`, `{{PLATFORM_SKIP_LINES}}`

## What to Create

### 1. `tests/run_tests.ps1`

PowerShell script that replicates the exact behavior of `run_tests.sh`:

- Use the same directory structure: `tests/logs/`, `prompts/ready/`
- Use the same file naming: `tests/logs/<basename>.log`, `prompts/ready/PROMPT_fix_<basename>.md`, `prompts/ready/PROMPT_run_<basename>.md`
- Use the same templates: `tests/prompt_template.md`, `tests/platform_skip_template.md`
- Replace `{{PLACEHOLDER}}` strings identically
- Use `python -m pytest` (not `python3` — Windows convention)
- Set `$REPO_ROOT` relative to the script's own location (same as `run_tests.sh` does)
- Handle the case where python is `python3` or `python` (check which exists)

The log files and prompt files must be **byte-for-byte compatible** with the Linux versions so they can be committed and pushed via git to the same repo. Use UTF-8 encoding with LF line endings (not CRLF).

### 2. Windows Polling Service

Implement a PowerShell script (`deploy/install_service.ps1`) that registers a Windows service responsible for:

- **Polling:** Continuously (e.g., every minute) checking the `workorders/ready` directory for new test files (`tests/run_tests.ps1` logic still applies here for identifying runnable tests).
- **Execution:** When new tests are found, executing `tests/run_tests.ps1` in a way that *does not* create a pop-up window or interrupt the user.
- **Background Operation:** The service must run silently in the background.
- **Service Management:** The script should handle:
    - Installation of the service.
    - Starting the service.
    - Stopping the service.
    - Checking if the service is already installed/running.

This may involve using `nssm.exe` (Non-Sucking Service Manager) or native PowerShell cmdlets to create and manage the Windows service. NSSM is already available in `bin/nssm.exe`.

### 3. `deploy/uninstall_service.ps1`

A simple PowerShell script to uninstall and stop the Windows service.

## Testing

1. Run `tests/run_tests.ps1` manually on a Windows machine
2. Verify it creates log files in `tests/logs/`
3. Deliberately make a test fail, delete its log, re-run, verify prompt appears in `prompts/ready/`
4. Verify the prompt content matches what the Linux version would produce
5. Run `deploy/install_service.ps1`, verify the service is installed and running
6. Wait 2 minutes, verify the runner executed (check `tests/logs/` for new files), and no windows popped up.

## Files to Create

- `tests/run_tests.ps1` — the Windows test runner
- `deploy/install_service.ps1` — Windows Service registration and management
- `deploy/uninstall_service.ps1` — Windows Service cleanup

## Important Notes

- Do NOT modify `run_tests.sh` — it works fine on Linux
- Use UTF-8 with LF line endings in all generated files (logs and prompts) so git diffs are clean across platforms
- The script must work on PowerShell 5.1+ (ships with Windows 10/11) — no PowerShell 7 features
- `python` on Windows may be `python` or `python3` or `py -3` — try all three
- The script should `cd` to `$REPO_ROOT` before running pytest, same as the bash version does

DEAD END
