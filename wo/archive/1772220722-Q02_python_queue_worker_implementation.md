# Q02: Pure Python Queue Worker Implementation

## Objective

Implement a pure Python queue-worker that replaces complex batch/bash scripts with elegant cross-platform code.

## Current Challenges

- `queue_worker_service.py` spawns agents via shell scripts (batch on Windows, bash on Unix)
- Path conversion Windows→WSL is fragile (done in `_get_path_for_shell()`)
- Different spawn logic per platform (batch vs. bash)
- Difficult to debug failures across platforms

## Solution Architecture

Implement pure Python queue-worker that:
1. Detects platform at runtime (Windows/Linux/macOS)
2. Uses platform.json for cross-platform paths
3. All subprocess calls use Python (no shell scripts)
4. All path handling via `pathlib.Path`
5. Unified code path for all platforms

## Core Queue Processing Loop

```
FOREVER:
  1. Check any agent running?
     - Scan agents/*/queue/work/ for .pid files
     - Use is_process_alive() to check if PIDs are live
     - If any alive → exit cycle (one-at-a-time rule)

  2. Process queue/in/
     - Find agents/<agent>/queue/in/*.md files (first one)
     - Move to queue/work/
     - Create: agents/<agent>/queue/work/<file>.pid
     - Spawn: Python subprocess to run agent

  3. Process queue/work/
     - Find completed agents (PID file exists but process dead)
     - Check WIP file for COMPLETE
     - Move results: queue/work/ → queue/out/, wip/ → done/
     - Git commit + refresh-maps
     - Log success/failure
```

## Files to Create/Modify

### Modify: `packages/csc-service/csc_service/infra/queue_worker.py`

**New QueueWorker class** replacing service-based pattern:

```python
class QueueWorker:
    """Standalone queue processor (can run in subprocess or daemon)."""

    def __init__(self, project_root=None):
        """Initialize with platform detection."""

    def cycle(self):
        """Run one queue processing cycle."""

    def process_queue_in(self):
        """Scan agents/*/queue/in/ for new work."""

    def process_queue_work(self):
        """Check for completed agents, move results."""

    def _spawn_agent_python(self, agent_name, workorder_path):
        """Spawn agent via pure Python subprocess."""
```

### New: `packages/csc-service/csc_service/infra/queue_logger.py`

Simple JSON-based logger for queue operations.

## Platform Detection & Path Handling

### Cross-Platform Process Spawning

```python
def _spawn_agent_python(self, agent_name, workorder_path):
    """Pure Python agent spawning."""
    is_windows = os.name == 'nt'
    cmd = [sys.executable, str(run_agent_py), str(workorder_path)]

    if is_windows:
        popen_kwargs = {
            'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP
        }
    else:
        popen_kwargs = {
            'start_new_session': True
        }

    proc = subprocess.Popen(cmd, cwd=str(self.project_root), **popen_kwargs)
    return proc.pid
```

## Acceptance Criteria

- ✅ No batch/bash scripts in queue processing logic
- ✅ Cross-platform process spawning (Windows/Linux/macOS)
- ✅ Unified code path (not branching for platform)
- ✅ Platform.json loaded and used correctly
- ✅ One-agent-at-a-time enforcement
- ✅ PID tracking and process alive check
- ✅ Proper logging
- ✅ Git operations working on all platforms
- ✅ Unit tests for core loops

## Dependencies

- Requires Q01 (queue directories exist)
- Requires Q03 (run_agent.py implementation)


--- AUDIT [2026-02-27 13:22] ---
INCOMPLETE
Pending:
  - NO WORK LOG section present - no agent activity logged
  - NO COMPLETE marker - file ends at dependencies section
  - No evidence of actual implementation in csc_service/infra/queue_worker.py
  - No evidence of queue_logger.py creation
  - No evidence of platform detection code being integrated
  - No evidence of unit tests being written
  - No git commits or integration work logged
  - This is a design/planning document only, not an implementation record
This is a well-written design specification but lacks any work log showing implementation was actually completed - it reads as a planning document, not a completed workorder.


DEAD END - Superseded by current queue_worker.py and run_agent.py implementation
