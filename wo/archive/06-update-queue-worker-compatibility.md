# Update Queue Worker for Backward Compatibility

## Objective

Update the queue worker to find `agent-wrapper` with fallback to `dc-agent-wrapper` for backward compatibility.

## Context

The queue worker (`packages/csc-shared/services/queue_worker_service.py`) needs to find the wrapper script. During transition, it should prefer `agent-wrapper` but fall back to `dc-agent-wrapper` if needed.

## Tasks

### 1. Update find_wrapper() Method

**File:** `packages/csc-shared/services/queue_worker_service.py`

**Replace the `find_wrapper()` method (around lines 66-82):**

```python
def find_wrapper(self):
    """Find the wrapper script (agent-wrapper with fallback to dc-agent-wrapper)."""
    wrapper_candidates = [
        # Prefer new wrapper name
        self.BIN_DIR / "agent-wrapper",
        self.BIN_DIR / "agent-wrapper.py",
    ]

    if self.IS_WINDOWS:
        wrapper_candidates.extend([
            self.BIN_DIR / "agent-wrapper.bat",
            self.BIN_DIR / "agent-wrapper.exe",
        ])

    # Fallback to old name for backward compatibility
    wrapper_candidates.extend([
        self.BIN_DIR / "dc-agent-wrapper",
        self.BIN_DIR / "dc-agent-wrapper.py",
    ])

    if self.IS_WINDOWS:
        wrapper_candidates.extend([
            self.BIN_DIR / "dc-agent-wrapper.bat",
            self.BIN_DIR / "dc-agent-wrapper.exe",
        ])

    for wrapper in wrapper_candidates:
        if wrapper.exists():
            self.log(f"Found wrapper: {wrapper}")
            return str(wrapper)

    self.log("ERROR: No wrapper script found")
    return None
```

## Verification

```bash
# Check find_wrapper method updated
grep -A 30 "def find_wrapper" packages/csc-shared/services/queue_worker_service.py

# Verify new wrapper checked first
grep "agent-wrapper" packages/csc-shared/services/queue_worker_service.py | head -1

# Verify fallback exists
grep "dc-agent-wrapper" packages/csc-shared/services/queue_worker_service.py

# Test queue worker finds wrapper
queue-worker cycle 2>&1 | grep "Found wrapper"

# Verify it uses agent-wrapper (not dc-agent-wrapper)
queue-worker cycle 2>&1 | grep "agent-wrapper" | grep -v "dc-agent"
```

## Completion Criteria

- [ ] `find_wrapper()` method updated to check new wrapper first
- [ ] Windows platform checks for `.bat` and `.exe` extensions
- [ ] Fallback to `dc-agent-wrapper` for backward compatibility
- [ ] Log message confirms which wrapper was found
- [ ] Returns `None` if no wrapper found
- [ ] Queue worker successfully finds and uses `agent-wrapper`

1. Check find_wrapper has backward compat
2. Check fallback to old wrapper
3. Check Windows platform handling
