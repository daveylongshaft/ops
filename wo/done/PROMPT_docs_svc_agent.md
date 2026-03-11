# Document & Test: agent service

## Task
1. Read `services/agent_service.py` — document every public method
2. Add an `agent` section to `docs/services.md` under a new "Workflow & Automation Services" heading (create if missing)
3. Write `tests/test_agent_service.py`

## Documentation
- Document every command: list, select, assign, status, stop, tail
- Explain the full assign workflow: move to wip, git sync, spawn subprocess, WIP journaling
- Document supported backends (claude, gemini) and how detection works
- Explain the stale watchdog (STALE_THRESHOLD_SECS, warns in status)
- Explain --append-system-prompt enforcement for WIP journaling
- Command syntax: `AI <token> agent <method> [args]`

## Tests
- Mock the server instance, mock subprocess.Popen and shutil.which
- Test list/select with mocked agent availability
- Test assign flow: prompt found, moved to wip, process spawned, state tracked
- Test assign errors: agent already running, prompt not found, agent not available
- Test status output with/without running process
- Test stop with mocked os.kill
- Test tail with a real tempfile as WIP
- Test stale watchdog: old mtime triggers warning
- Use `unittest.TestCase`, use tempdir for prompt dirs
- File: `tests/test_agent_service.py`

read services/agent_service.py
read docs/services.md
update agent section in docs/services.md
update docs/services.md
write tests/test_agent_service.py
commit
move
push
