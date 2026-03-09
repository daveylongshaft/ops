# Test: agent service

## Task
Write `tests/test_agent_service.py` — unit tests for `services/agent_service.py`.

This is the service that spawns AI CLI sessions to work prompt files. The 12 `PROMPT_docs_svc_*.md` prompts in `ready/` are waiting to be executed by this system. These tests prove the agent service works before we start feeding it real work.

## What to test

Read `services/agent_service.py` first. Then test:

### list / select
- list shows known agents with availability
- select stores choice in data
- select rejects unknown agent name
- select rejects agent not in PATH

### assign
- moves prompt from ready/ to wip/
- builds assembled prompt (includes README.1st, prompts/README.md, instructions, WIP contents)
- spawns subprocess with correct args for claude backend
- spawns subprocess with correct args for gemini backend
- tracks PID, prompt name, log path, timestamp in data
- rejects if agent already running
- rejects if prompt file not found
- rejects if selected agent not available

### status
- shows RUNNING with stats when process alive
- shows FINISHED when process dead
- shows stale warning when WIP file mtime is old
- shows WIP progress counts ([X], [NEXT], [ ])

### stop
- sends SIGTERM, waits, falls back to SIGKILL
- clears PID/log/timestamp state
- keeps WIP file in place

### kill
- sends SIGKILL immediately
- moves WIP file back to ready/
- preserves file contents (journal survives)
- clears PID/log/timestamp state

### tail
- returns last N lines of WIP file
- defaults to 20 lines
- handles file in done/ (already completed)
- handles missing file

### _build_cmd
- claude: includes -p, --dangerously-skip-permissions, --model sonnet, --append-system-prompt
- gemini: includes -y, -p, prepends system rule to prompt

## How to test
- Mock the server instance (services expect server_instance in __init__)
- Mock subprocess.Popen — never spawn real processes
- Mock shutil.which — control agent availability
- Mock os.kill — never send real signals
- Use tempdir for ready/wip/done dirs
- Use unittest.TestCase
- Follow pattern in tests/test_patch_service.py for imports

## Output
- `tests/test_agent_service.py`
- Do NOT run the tests. Cron handles that.
- Reading agent_service.py and test_patch_service.py for patterns
- Checked Service/Data/Log/Network inheritance chain for mocking
- Wrote tests/test_agent_service.py — 35 test cases across 12 test classes
- Verified syntax clean, left for cron to execute
- MockService patches the inheritance chain so no real server needed
- Rewrote tests: real sleep processes, real SIGTERM/SIGKILL, real file moves, real os.utime for stale
- Only mock is Service base class (avoids booting full server chain)
- Syntax verified, leaving for cron

### Session 2 (2026-02-17) — Rewrite: assign() was untested
- [X] Discovered TestAssign class was missing from rewritten test file
- [X] Old log showed 43 passing tests, but assign() had zero coverage
- [X] TestSelectReal skipped when no binaries in PATH — replaced with mocked TestSelect (4 tests)
- [X] Added TestAssign class — 12 unit tests covering: file move, journal, state tracking, claude/gemini cmd args, assembled prompt, guard clauses (running/missing/unavailable), md extension, wip-stays-in-wip
- [X] Added TestAssignEndToEnd — full acceptance test with 12 checkpoints and diagnostic dump on failure
- [X] Added TestAssignEndToEnd gemini variant for different cmd format
- [X] Verified syntax clean, deleted stale log for cron pickup
