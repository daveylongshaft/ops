---
agent: sonnet
platform: [linux, windows, android]
---

# Enhance dc-agent-wrapper with Monitoring and Verification

## Objective

Enhance `bin/dc-agent-wrapper` with file growth monitoring, STATUS: COMPLETE checking, test verification, and single-agent enforcement.

## Files to Modify

- `bin/dc-agent-wrapper` (324 lines) — the only file to change

## Current Behavior

The wrapper currently does a simple `proc.wait(timeout=1800)` — no liveliness check, no content inspection, exit-code-only success detection.

## Required Changes

### 1. Polling Loop (replace proc.wait)

Replace the `proc.wait(timeout=1800)` block (lines ~295-304) with a polling loop:

```python
POLL_INTERVAL = 30       # seconds between checks
STALL_TIMEOUT = 180      # 3 minutes no growth → kill
MAX_RUNTIME = 1800       # 30 minute hard cap
```

- Poll `proc.poll()` every `POLL_INTERVAL` seconds
- Track elapsed time; kill at `MAX_RUNTIME`
- Between polls, check WIP file size (see #2)

### 2. File Growth Monitoring

During the polling loop, track the WIP file's size:

```python
last_size = wip_file_path.stat().st_size if wip_file_path.exists() else 0
last_growth_time = time.time()
```

Each poll iteration:
- Read current WIP file size
- If size increased: update `last_size` and `last_growth_time`
- If `time.time() - last_growth_time > STALL_TIMEOUT`:
  - Log: "Agent stalled — no file growth for 3 minutes"
  - Kill the process
  - Set `agent_status = "stalled"`

### 3. STATUS: COMPLETE Checking

After the process exits (regardless of exit code), read the WIP file and check the last non-empty line:

```python
def check_wip_status(wip_file_path):
    """Read last non-empty line of WIP file. Return True if STATUS: COMPLETE."""
    try:
        lines = Path(wip_file_path).read_text(encoding='utf-8').splitlines()
        for line in reversed(lines):
            stripped = line.strip()
            if stripped:
                return stripped == "STATUS: COMPLETE"
        return False
    except Exception:
        return False
```

Decision logic after process exits:
- If `check_wip_status()` returns True → proceed to test verification (#4)
- If False → set `agent_status = "incomplete"`, move to ready/ for resumption

### 4. Test Verification

When STATUS: COMPLETE is found, check if test files were modified:

```python
def check_tests_written():
    """Check if any test files were modified in the working tree."""
    result = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=str(CSC_ROOT), capture_output=True, text=True
    )
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=str(CSC_ROOT), capture_output=True, text=True
    )
    all_changed = result.stdout + staged.stdout
    for line in all_changed.splitlines():
        if line.strip().startswith("tests/test_"):
            return True
    return False
```

Decision logic:
- If tests found → `agent_status = "complete"`, move to done/
- If no tests found:
  - Append `"\n--- TESTS REQUIRED ---\nWrite tests for all changes. See tests/ for examples.\n"` to the WIP file
  - Log: "No tests written — restarting agent"
  - Allow ONE restart (track retry count), then move to ready/ if still no tests

### 5. Single-Agent Enforcement

Add a function that scans `wip/*.md` files for `AGENT_PID:` lines and checks if those PIDs are alive:

```python
def check_existing_agents(current_prompt):
    """Refuse to start if another live agent is working in wip/."""
    for wip_file in WIP_DIR.glob("*.md"):
        if wip_file.name == current_prompt:
            continue  # Skip our own prompt
        try:
            content = wip_file.read_text(encoding='utf-8')
            for line in content.splitlines():
                if line.strip().startswith("AGENT_PID:"):
                    pid_str = line.split(":", 1)[1].strip()
                    try:
                        pid = int(pid_str)
                        if is_pid_alive(pid):
                            return wip_file.name, pid
                    except ValueError:
                        pass
        except Exception:
            pass
    return None, None

def is_pid_alive(pid):
    """Check if a process is alive. Cross-platform."""
    try:
        if os.name == 'nt':
            # Windows: tasklist filter
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True, text=True
            )
            return str(pid) in result.stdout
        else:
            os.kill(pid, 0)  # Signal 0 = check existence
            return True
    except (OSError, ProcessLookupError):
        return False
```

Call `check_existing_agents()` at the start of `main()`, before git pull. If another agent is alive:
- Log: "Another agent (PID {pid}) is working on '{filename}'. Aborting."
- Move our prompt back to ready/
- Exit with code 1

### 6. Stamp AGENT_PID in WIP

After launching the process, append the PID to the WIP file:

```python
with open(wip_file_path, 'a', encoding='utf-8') as f:
    f.write(f"\nAGENT_PID: {proc.pid}\n")
```

## Integration Points

The updated `agent_status` values and their effects:
- `"complete"` → move to done/, commit as `feat:`
- `"incomplete"` → move to ready/ (no STATUS: COMPLETE)
- `"stalled"` → move to ready/ (no file growth)
- `"failed"` → move to ready/ (process error)

The existing `move_prompt()`, `git_commit_push()`, `build_agent_cmd()`, `find_agent()`, and `ensure_ollama_running()` functions should remain unchanged.

## Cross-Platform Notes

- Use `os.name == 'nt'` for Windows PID checking
- `Path.stat().st_size` works cross-platform
- File encoding: always use `encoding='utf-8'`

## Work Log

Journal every step to this file using:
```bash
echo '<step>' >> prompts/wip/sonnet-enhance-dc-agent-wrapper.md
```

## Success Criteria

- Polling loop replaces proc.wait with 30s interval checks
- Stalled agents (no WIP growth for 3 min) get killed and moved to ready/
- Agents without STATUS: COMPLETE get moved to ready/
- Missing tests trigger one restart with appended instruction
- Concurrent agent launch is blocked when another agent PID is alive
- All cross-platform: works on Windows (MSYS2), Linux, Android

STATUS: COMPLETE
