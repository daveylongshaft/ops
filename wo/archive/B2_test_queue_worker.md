# Phase B2: Write Tests for Queue Worker

## Task

Create unit tests for the queue-worker script to verify all functionality.

## Requirements

**File:** `tests/test_queue_worker.py`

Test coverage:
1. `check_pid()` - verify PID detection works
2. `process_incoming()` - verify queue/in/ scanning
3. `process_completed()` - verify completion detection
4. Queue file movement logic
5. PID file creation/deletion
6. Wrapper spawning

## Implementation

```python
import pytest
from pathlib import Path
from bin.queue_worker import check_pid, process_incoming, process_completed

def test_check_pid_alive(running_process):
    """Test PID check for running process."""
    assert check_pid(running_process.pid) == True

def test_check_pid_dead():
    """Test PID check for dead process."""
    assert check_pid(99999) == False

def test_process_incoming(tmp_path):
    """Test processing new prompts from queue/in/."""
    # Create test prompt in queue/in/
    # Run process_incoming()
    # Verify moved to queue/work/
    # Verify .pid file created
    pass

def test_process_completed(tmp_path):
    """Test processing completed work."""
    # Create test prompt in queue/work/ with dead PID
    # Run process_completed()
    # Verify prompt cleaned up
    # Verify .pid file deleted
    pass
```

## Acceptance

- All tests pass
- Coverage > 80%
- Edge cases handled (missing files, invalid PIDs)

## Work Log
1. Test queue worker exists

---

DEAD END
