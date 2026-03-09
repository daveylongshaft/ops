# Redesign Queue-Worker and agent_service.assign()

## Task

Redesign the queue-worker system to properly integrate with agent_service.assign() via a template-based approach. The queue-worker should handle all agent lifecycle management: pickup, execution, PID tracking, and cleanup.

## Current Problem

The old benchmark queue system (B1, B2, C1, F1) was disconnected from the actual agent_service.assign() workflow. It needs a complete redesign to:
1. Integrate with agent_service.assign() in agent_service.py
2. Use a template-based approach for queue workorders
3. Properly handle agent PID tracking
4. Implement reliable cleanup and restart logic

## System Design

### Phase 1: agent_service.assign() Changes

**File:** `packages/csc-shared/services/agent_service.py`

When `agent_service.assign(prompt_filename)` is called:
1. Move prompt from `workorders/ready/{prompt}` to `workorders/wip/{prompt}`
2. Call `create_queue_workorder()` with:
   - `wip_path`: Path to the wip workorder file
   - `agents_dir`: Path to the agents directory
   - `agent_name`: Name of the agent
3. Create a template workorder in `agents/{agent}/queue/in/` directory

**New method to add:**
```python
def create_queue_workorder(self, wip_path, agents_dir, agent_name):
    """Create a template workorder in the agent's queue/in directory."""
    template = f"""# Queue Workorder

Agent: {agent_name}
WIP: {wip_path}

## Instructions

Read the WIP file at {wip_path} and complete the task.

Journal all work to the WIP file using echo >> before each step.

When complete, add "COMPLETE" at the end of the WIP file.

---

## Work Log
"""

    queue_in_dir = Path(agents_dir) / agent_name / "queue" / "in"
    queue_in_dir.mkdir(parents=True, exist_ok=True)

    # Use timestamp-based filename for uniqueness
    import time
    queue_file = queue_in_dir / f"{int(time.time())}-workorder.md"
    queue_file.write_text(template, encoding='utf-8')

    return queue_file
```

### Phase 2: queue-worker Script

**File:** `bin/queue-worker`

The queue-worker script runs every 2 minutes (via cron/Task Scheduler) and:

1. **Poll for new workorders in `agents/*/queue/in/`**
   - Find all `.md` files in queue/in/
   - Move each to `queue/work/`

2. **Spawn agent process**
   - Run `agents/{agent}/run_agent` script
   - Pass queue/work/orders.md path
   - Capture and save PID to `.pid` file in queue/work/

3. **Poll for completed work in `agents/*/queue/work/`**
   - Check each `.pid` file
   - If PID no longer running:
     - Move workorder to `queue/done/`
     - Update git repo
     - Clean up `.pid` file

**Pseudocode:**
```python
def process_incoming():
    """Check agents/*/queue/in/ for new workorders."""
    for agent_dir in agents_root.glob("*/"):
        queue_in = agent_dir / "queue" / "in"
        for workorder in queue_in.glob("*.md"):
            # Move to work
            queue_work = agent_dir / "queue" / "work"
            queue_work.mkdir(parents=True, exist_ok=True)
            work_file = queue_work / workorder.name
            workorder.rename(work_file)

            # Spawn agent
            agent_name = agent_dir.name
            run_agent_script = agent_dir / "run_agent"
            pid = spawn_process(run_agent_script, work_file)

            # Save PID
            pid_file = queue_work / f"{work_file.stem}.pid"
            pid_file.write_text(str(pid))

def process_completed():
    """Check agents/*/queue/work/ for completed workorders."""
    for agent_dir in agents_root.glob("*/"):
        queue_work = agent_dir / "queue" / "work"
        for pid_file in queue_work.glob("*.pid"):
            pid = int(pid_file.read_text())
            if not is_process_running(pid):
                # Process is done, clean up
                workorder = pid_file.parent / pid_file.stem
                queue_done = agent_dir / "queue" / "done"
                queue_done.mkdir(parents=True, exist_ok=True)
                workorder.rename(queue_done / workorder.name)
                pid_file.unlink()

                # Update git
                run_git_commit()
```

### Phase 3: run_agent Script

**File:** `agents/{agent_name}/run_agent`

This script is called by queue-worker with a queue workorder path:

```bash
#!/bin/bash
WORKORDER_PATH=$1
REPO_DIR=$(pwd)  # csc repo root
AGENT_NAME=$(basename $(dirname $(dirname $0)))

# Read instructions from workorder
INSTRUCTIONS=$(cat "$WORKORDER_PATH")

# Change to repo directory
cd "$REPO_DIR"

# Run the agent with instructions piped in
# The agent processes the instructions and journals work to the WIP file
echo "$INSTRUCTIONS" | claude --dangerously-skip-permissions \
    @workorders/README.md @tools/INDEX.txt \
    "Process this workorder and journal all work to the WIP file specified in the instructions."
```

## Implementation Steps

1. **Update agent_service.py:**
   - Add `create_queue_workorder()` method
   - Call it from `assign()` method
   - Ensure prompt moves to wip/ first

2. **Update or create bin/queue-worker:**
   - Implement `process_incoming()` function
   - Implement `process_completed()` function
   - Implement main loop that calls both
   - Test with print statements

3. **Create agents/{agent}/run_agent scripts:**
   - Create for each agent (claude, gemini, chatgpt, ollama-*)
   - Each reads workorder and pipes to agent CLI
   - Records work to WIP file

4. **Verify integration:**
   - Call `agent_service.assign()`
   - Verify workorder appears in agents/queue/in/
   - Verify queue-worker picks it up
   - Verify agent executes and PID is tracked
   - Verify cleanup on completion

## Acceptance Criteria

- [ ] `agent_service.assign()` moves prompt to wip/ and creates queue workorder
- [ ] `bin/queue-worker` polls and finds workorders in agents/*/queue/in/
- [ ] Workorders moved to queue/work/ and agent spawned
- [ ] PID files created and tracked
- [ ] Completed work detected and cleaned up
- [ ] Git repo updated after completion
- [ ] No prompts stuck in wip/ or queue/work/
- [ ] Works cross-platform (Windows, Linux, macOS, Android)

## Dependencies

- Depends on: `agent_service.py` exists and is functional
- Requires: agents/{agent}/run_agent scripts created
- Platform support: Windows (Task Scheduler), Linux (cron), macOS (cron)

## Notes

- Queue workorder path must be absolute (for cross-platform reliability)
- PID tracking works on all platforms
- Use pathlib.Path for all path operations
- Ensure agents/*/queue/{in,work,done}/ directories created as needed
- Test on Windows first (most complex platform)

## Work Log


--- AUDIT [2026-02-27 13:22] ---
INCOMPLETE
Pending:
  - Could not parse structured response
```json
{
  "verdict": "INCOMPLETE",
  "evidence": [],
  "pending": [
    "No work log entries showing actual implementation of agent_service.assign() changes",
    "No evidence that bin/queue-worker 


DEAD END - Queue worker and agent assign redesigned in current codebase
