# Workorder: tmp/ Directory Path Restructure

## Summary
Fix agent temp directory structure so spawn_cwd = project root (CSC_ROOT) and agents can access both code repos and work files via relative paths from project root.

## Root Causes
- `csc_agent_work` = `temp_root / "csc"` (extra subdir not needed)
- `spawn_cwd` = temp clone dir (agents can't reach ops/ via relative path)
- `<agent_repo_rel_path>` set at assign-time when clone path isn't known yet
- orders.md-template says "running from /opt/" (wrong)

## Benefits
- All agent work files accessible via relative path from CSC_ROOT
- Agents can't accidentally escape via `../../../` (they have full context at root)
- Gemini (which can't traverse to parent dir) can still reach all needed files
- Consistent path handling across all agent code

---

## Implementation

### 1. Update platform.py (~line 709)

**File**: `irc/packages/csc-service/csc_service/shared/platform.py`

Find line:
```python
runtime["csc_agent_work"] = str(temp_root / "csc")
```

Change to:
```python
runtime["csc_agent_work"] = str(temp_root)
```

**Why**: Remove the extra "csc" subdirectory. Clones will now go to `C:\csc\tmp\clones\...` not `C:\csc\tmp\csc\clones\...`

---

### 2. Update platform.json

**File**: `etc/platform.json`

Find:
```json
"csc_agent_work": "C:\\csc\\tmp\\csc",
```

Change to:
```json
"csc_agent_work": "C:\\csc\\tmp",
```

OR: Just let platform.py regenerate it on next startup (the code change above will auto-fix it).

---

### 3. Update queue_worker.py - spawn_cwd

**File**: `irc/packages/csc-service/csc_service/infra/queue_worker.py`

Find line ~913:
```python
spawn_cwd = str(agent_repo) if agent_repo else str(CSC_ROOT)
```

Change to:
```python
spawn_cwd = str(CSC_ROOT)
```

**Why**: Agents run from project root so they can reference `tmp/clones/...` and `ops/wo/wip/...` as relative paths.

---

### 4. Update queue_worker.py - Inject clone path into orders.md

**File**: `irc/packages/csc-service/csc_service/infra/queue_worker.py`

In function `spawn_agent()`, after the clone is created (~line 925) and before the Popen call (~line 940), add:

```python
# Inject the actual relative clone path into orders.md so agent knows where to work
try:
    orders_work = agent_dir / "queue" / "work" / "orders.md"
    if orders_work.exists():
        content = orders_work.read_text(encoding="utf-8")
        # Make path relative from CSC_ROOT with forward slashes (for portability)
        clone_rel = str(agent_repo.relative_to(CSC_ROOT)).replace("\\", "/")
        content = content.replace("<agent_repo_rel_path>", clone_rel)
        orders_work.write_text(content, encoding="utf-8")
except Exception as e:
    log(f"WARNING: Failed to inject clone path into orders.md: {e}")
```

**Why**: At assign-time, the timestamped clone path isn't known. Now that queue_worker created it, inject the real path so agents know where their code repo is.

---

### 5. Update agent_service.py - Don't replace agent_repo_rel_path

**File**: `irc/packages/csc-service/csc_service/shared/services/agent_service.py`

In function `_run_generate_orders_md_script()`, find the line:
```python
content = content.replace("<agent_repo_rel_path>", repo_path)
```

Delete this line entirely (or comment it out).

**Why**: queue_worker will handle this replacement with the actual clone path. If we replace it here with PROJECT_ROOT, agents won't know where their temp clone is.

---

### 6. Update orders.md-template text

**File**: `ops/agents/templates/orders.md-template`

Find:
```
You are an AI coding agent running from /opt/.
```

Replace with:
```
You are an AI coding agent. Your working directory is the project root.
```

And update the "Code repo" line to clarify:
```
- **Code repo**: `<agent_repo_rel_path>/` — your isolated clone of irc.git (relative from project root). Do all code edits here.
```

**Why**: Correct the documentation and clarify that the path is relative from project root.

---

## Verification

After all changes:

1. **Check platform.json**: `cat etc/platform.json | grep csc_agent_work` should show `C:\\csc\\tmp` (not `...\\tmp\\csc`)

2. **Assign a test workorder**:
   ```bash
   agent select haiku
   wo add tmp-test : Test cleanup temp path
   # Then edit the file to have some work instruction
   agent assign tmp-test.md
   ```

3. **Check orders.md** in `ops/agents/haiku/queue/work/orders.md`:
   - Should say "working directory is project root"
   - Should have `<agent_repo_rel_path>` replaced with something like `tmp/clones/haiku/...`

4. **Check spawn**: `csc-ctl cycle queue-worker` should spawn with cwd=`C:\csc`, not cwd=temp clone

5. **Agent runs**: `agent tail` should show agent working in the temp clone (via relative path from root)

---

## Edge Cases

- If an agent is already running when you apply these changes, kill it: `agent kill`
- The next `csc-ctl cycle queue-worker` will create a fresh clone with the new path structure
- Old clones in `C:\csc\tmp\csc\clones\` can be deleted after verifying new clones work: `rm -rf C:\csc\tmp\csc\clones`
- If platform.json doesn't update, manually edit it or delete `etc/platform.json` to force regeneration on startup

---

## Summary of Changes
- platform.py: 1 line change
- platform.json: 1 line change (or regenerate)
- queue_worker.py: 2 changes (1 line + 10 lines)
- agent_service.py: 1 line deletion
- orders.md-template: 2 text edits

Total: ~16 lines of code changes
