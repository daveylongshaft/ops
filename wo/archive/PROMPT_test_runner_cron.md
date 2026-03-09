# Task: Build Cron Test Runner

## Goal

Create `tests/run_tests.sh` and `tests/prompt_template.md` — a cron-driven test runner that:
1. Scans `tests/test_*.py` for files without a matching `tests/logs/*.log`
2. Runs the test, creating the log (always, pass or fail)
3. If FAILED lines in log: fills template, writes `prompts/ready/PROMPT_fix_test_<name>.md`
4. Log exists = skip (prevents infinite prompts on repeated failures)

## The Cycle

Cron → run test → create log → FAILED? → create prompt → AI fixes → human deletes log → cron retests

## Files to Create
- `tests/run_tests.sh`
- `tests/prompt_template.md`
- `tests/logs/` directory (mkdir -p)

## Rules
- Log file is the lock — exists means don't retest, don't re-prompt
- Template must include: test file name, FAILED lines, path to full log
- Script must be idempotent (safe to run repeatedly)
- Update CLAUDE.md testing section with new rules

Verified complete.
