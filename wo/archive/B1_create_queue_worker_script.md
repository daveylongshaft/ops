# Phase B1: Create Queue Worker Script

## Task

Create the queue-worker script that monitors agent queues and processes benchmark tasks.

## Requirements

**File:** `bin/queue-worker` (Python script)
**File:** `bin/queue-worker.bat` (Windows wrapper)

The worker runs periodically (via Task Scheduler on Windows, cron on Linux) and:
1. Checks all `agents/*/queue/in/` for new prompts
2. Moves prompts to `queue/work/` and spawns wrapper
3. Saves wrapper PID to `.pid` file
4. Checks `queue/work/` for completed tasks (dead PIDs)
5. Archives results and cleans up

## Implementation

Create `bin/queue-worker` with:

```python
#!/usr/bin/env python3
"""Queue worker for benchmark system - runs periodically via scheduler."""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "packages"))

def check_pid(pid):
    """Check if PID is still running."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False

def process_incoming():
    """Check agents/*/queue/in/ for new work."""
    # Scan for prompts in queue/in/
    # Move to queue/work/
    # Spawn wrapper, save PID
    pass

def process_completed():
    """Check agents/*/queue/work/ for completed work."""
    # Find prompts with .pid files
    # Check if PID is dead
    # If dead: process completion, archive, cleanup
    pass

def main():
    print("[queue-worker] Starting queue check...")
    process_incoming()
    process_completed()
    print("[queue-worker] Queue check complete")

if __name__ == "__main__":
    main()
```

Create `bin/queue-worker.bat`:
```batch
@echo off
python C:\csc\bin\queue-worker %*
```

## Acceptance

- Script created and executable
- Runs without errors
- Can detect prompts in queue/in/
- Can spawn wrapper processes
- Can detect completed work

## Work Log
1. Create queue worker script
Note: queue_worker_service.py already exists in packages/csc-shared/services/
2. Verify queue worker has required methods

---

DEAD END
