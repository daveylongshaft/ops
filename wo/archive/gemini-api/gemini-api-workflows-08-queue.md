---
urgency: P2
agent: sonnet
requires: python,google-genai,queue-worker-integration
tags: queue-worker,integration,automation
blockedBy: gemini-api-workflows-03-batch-runner.md,gemini-api-workflows-04-tool-runner.md
---

# Workorder: Gemini Batch API - Queue-Worker Integration

## Context
Integrate Gemini batch processing into the existing CSC queue-worker pipeline. This allows Gemini workorders to be assigned and processed automatically, mirroring the existing Anthropic batch queue integration.

**Related:** Part 9 of 12-part series. Blocked by workorders 03 & 04. Enables full automation.

## Deliverables

### Create `bin/gemini-batch/gbatch_queue_run.py`

**CLI Usage:**
```
gbatch_queue_run.py [--config batch_config.json] [--agent gemini]
                     [--max-cycles 100] [--mode tool-loop|batch-api]
```

### 1. Integration Points

**Existing Systems to Integrate With:**
- `packages/csc-service/csc_service/infra/queue_worker.py` — polls `workorders/wip/` for in-progress workorders
- `packages/csc-service/csc_service/infra/agent_service.py` — manages agent selection and assignment
- `packages/csc-service/csc_service/infra/pm.py` — process manager for service supervision
- Workorder YAML frontmatter (urgency, agent, model, requires, blockedBy)

### 2. Main Loop

**`run_queue(config_path, agent_name, max_cycles, mode)` function:**

```python
def run_queue(
    config_path: str = "batch_config.json",
    agent_name: str = "gemini",
    max_cycles: int = 100,
    mode: str = "tool-loop"
):
    """
    Main queue worker loop for Gemini batch processing.
    Mirrors cbatch_queue_run.py pattern.
    """
```

**Flow:**
1. Load `batch_config.json` from `bin/gemini-batch/` via `common.load_config(config_path)`
2. Filter entries where `"provider": "gemini"` AND `"agent": agent_name`
3. For each cycle (up to max_cycles):
   a. Check `workorders/wip/` for in-progress Gemini workorders
   b. Check `workorders/ready/` for queued Gemini workorders (not assigned yet)
   c. For each workorder (in urgency order):
      - Load YAML frontmatter
      - Determine mode: explicit `--mode` or infer from workorder flags
      - If `--mode tool-loop` OR workorder has `requires: [file_io, shell]`:
        - Call `gbatch_tool_run.py <workorder>` (sync, full tool execution)
      - Else if `--mode batch-api`:
        - Call `gbatch_run.py run <single_workorder_config>` (async, text-only)
   d. On success:
      - Move workorder from `wip/` to `done/`
      - Append result to workorder file (optional)
   e. On failure:
      - Keep in `wip/` (or move to `ready/` for retry)
      - Log error to journal
   f. If journal file present (env var `CSC_WIP_FILE`): append progress
4. After all workorders complete:
   - If `--defer-git-sync` NOT set: run git add + commit + push
   - Log final stats: N completed, N failed, total cost
5. Sleep before next cycle (default: 60s)

---

### 3. Mode Selection Logic

**Infer mode from workorder:**
```python
def infer_mode(workorder_path: str) -> str:
    """
    Determine batch-api or tool-loop based on workorder requirements.
    """
    frontmatter = parse_yaml_frontmatter(workorder_path)
    requires = frontmatter.get("requires", [])

    # tool-loop needed if workorder requires file I/O or shell execution
    if "file_io" in requires or "shell" in requires or "git" in requires:
        return "tool-loop"

    # Otherwise use cheaper batch-api (text-only)
    return "batch-api"
```

**Explicit override:** `--mode tool-loop` forces tool-loop for all workorders

---

### 4. Agent Selection
- Load `agent_service.py` singleton (already exists in codebase)
- Call `agent_svc.select(agent_name)` to set active agent
- All workorders assigned to selected agent
- Logging: which agent is running which workorder

---

### 5. Workorder Processing

**Single Workorder Execution:**
```python
def process_workorder(
    workorder_path: str,
    mode: str,
    agent_name: str
) -> tuple[bool, str]:
    """
    Process one workorder.
    Returns (success: bool, message: str)
    """
    # 1. Create WIP journal file (env var CSC_WIP_FILE)
    # 2. Call mode-specific runner:
    if mode == "tool-loop":
        # Sync execution with tool loop
        return run_tool_loop_workorder(workorder_path)
    else:
        # Async batch submission + polling
        return run_batch_api_workorder(workorder_path)
    # 3. Append to journal on completion
    # 4. Return success status
```

**`run_tool_loop_workorder(workorder_path)` helper:**
- Call `gbatch_tool_run.py <workorder_path>`
- Capture stdout (final answer) and stderr (tool logs)
- Parse result tokens from stderr
- Return (True, result_text) or (False, error_message)

**`run_batch_api_workorder(workorder_path)` helper:**
- Call `gbatch_run.py run <config>` with `--async` (submit only, don't poll)
- Save job name to tracking file
- Poll in background or skip (async completion)
- Return (True, "Submitted job <name>") or (False, error)

---

### 6. Journal Integration
If env var `CSC_WIP_FILE` is set (by queue-worker):
- Append each milestone:
  ```
  [12:34:56] Starting workorder: sample-task.md
  [12:34:57] Mode: tool-loop
  [12:34:58] Agent: gemini
  [12:35:45] COMPLETE: Processed in 47 seconds
  Tokens: input=2345, output=678, cache_read=1024
  Cost: $0.009
  ```

---

### 7. Git Synchronization
After all workorders complete in a cycle:
- If `--defer-git-sync` NOT set:
  ```python
  subprocess.run(["git", "add", "."], cwd="/c/csc", check=True)
  subprocess.run(["git", "commit", "-m", "chore: Gemini batch auto-sync <timestamp>"], ...)
  subprocess.run(["git", "push"], ...)
  ```
- If `--defer-git-sync` set: skip (let parent process handle it)

---

### 8. Error Handling
- Network/API error: log, retry same workorder next cycle
- Timeout: move workorder back to `ready/` for retry
- Malformed workorder: log error, move to `hold/` for human review
- Missing model in MODELS dict: fall back to default

---

### 9. Configuration File
**`batch_config.json` entries for Gemini queue mode:**
```json
{
  "provider": "gemini",
  "agent": "gemini",
  "workorder": "workorders/ready/sample-task.md",
  "model": "gemini-2.5-flash",
  "builtin_tools": ["code_execution"],
  "added_at": "2026-03-03T12:00:00Z"
}
```

**Filtering:** Only entries matching `provider=gemini` AND `agent=gemini` are processed.

---

### 10. Entry Point
```python
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="batch_config.json")
    parser.add_argument("--agent", default="gemini")
    parser.add_argument("--max-cycles", type=int, default=100)
    parser.add_argument("--mode", choices=["tool-loop", "batch-api"], default=None)
    parser.add_argument("--defer-git-sync", action="store_true")
    args = parser.parse_args()

    run_queue(
        config_path=args.config,
        agent_name=args.agent,
        max_cycles=args.max_cycles,
        mode=args.mode
    )
```

---

## Testing Notes
- Unit test: `test_queue_mode_selection()` — verify tool-loop vs batch-api inference
- Unit test: `test_queue_process_single_workorder()` — mock tool runner, verify execution
- Unit test: `test_queue_git_sync()` — verify git commands run on completion
- Unit test: `test_queue_journal_append()` — verify journal file written with milestones
- Unit test: `test_queue_filter_config()` — verify only gemini entries processed

## Notes
- Synchronous queue processor (one workorder at a time)
- Can be run as a scheduled task (via pm.py) or standalone
- Mirrors existing `bin/claude-batch/cbatch_queue_run.py` pattern closely
- Integrates with queue-worker cycle system (no new infrastructure needed)
- All paths relative to `/c/csc/`
