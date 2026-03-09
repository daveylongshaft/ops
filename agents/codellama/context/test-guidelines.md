# Test Writing Guidelines

## CRITICAL: Agents WRITE Tests, Not RUN Them

**DO:**
- Write test files in `tests/` directory
- Create test cases for new features
- Update existing tests when changing behavior
- Document test purpose in docstring

**DO NOT:**
- Run pytest yourself
- Execute tests
- Delete test logs

**Why:** Cron handles all test execution. You write tests, cron runs them.

## Test Workflow

1. **You write the test** → `tests/test_<feature>.py`
2. **Cron runs it** → Generates `tests/logs/test_<feature>.log`
3. **If test fails** → Cron creates `workorders/ready/PROMPT_fix_test_<feature>.md`
4. **Next agent** → Picks up fix, reads log, fixes code
5. **Agent deletes log** → `rm tests/logs/test_<feature>.log`
6. **Cron re-runs** → New log generated

## Test File Structure

```python
#!/usr/bin/env python3
"""
Test suite for <feature>.

Purpose: <what this tests>
Coverage: <what scenarios are covered>
"""

import pytest
from pathlib import Path

# Setup
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def test_<feature>_<scenario>():
    """Test <specific behavior>."""
    # Arrange
    ...

    # Act
    ...

    # Assert
    assert expected == actual
```

## Test Naming

- **File:** `test_<component>.py`
- **Function:** `test_<feature>_<scenario>()`
- **Log:** `tests/logs/test_<component>.log`

## Common Patterns

### Testing IRC Server
```python
def test_server_handles_privmsg():
    """Test server routes PRIVMSG correctly."""
    # Import server module
    # Create test message
    # Send to server
    # Assert response
```

### Testing Agent Service
```python
def test_agent_assign_moves_workorder():
    """Test agent assign moves ready -> wip."""
    # Create test workorder in ready/
    # Call agent_service.assign()
    # Assert file moved to wip/
    # Cleanup
```

### Testing Queue Worker
```python
def test_queue_worker_detects_completion():
    """Test queue-worker detects COMPLETE marker."""
    # Create WIP with COMPLETE
    # Run detection logic
    # Assert moves to done/
```

## When to Write Tests

**Always write tests for:**
- New features
- Bug fixes (regression test)
- API changes
- Critical paths (server message handling, agent spawning)

**Test categories:**
- Unit tests: Individual functions
- Integration tests: Component interactions
- System tests: End-to-end workflows

## Reading Test Logs

If you're fixing a failed test:
1. Read `tests/logs/test_<name>.log`
2. Find the assertion failure
3. Understand what broke
4. Fix the code (not the test!)
5. Delete the log: `rm tests/logs/test_<name>.log`
6. Let cron re-run it

## Example: Complete Test File

```python
#!/usr/bin/env python3
"""
Test suite for API key manager.

Purpose: Verify API key rotation works correctly
Coverage: Load keys, rotate, persist state
"""

import pytest
import json
from pathlib import Path
from csc_shared.api_key_manager import APIKeyManager

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def test_api_key_manager_loads_keys(tmp_path):
    """Test APIKeyManager loads keys from config."""
    # Arrange: Create test config
    config = tmp_path / "api_keys.json"
    config.write_text(json.dumps({
        "anthropic_keys": ["key1", "key2"],
        "current_key_index": 0
    }))

    # Act: Load keys
    mgr = APIKeyManager(config)

    # Assert: Keys loaded correctly
    assert mgr.get_key_count() == 2
    assert mgr.current_index == 0
    assert mgr.get_current_key() == "key1"

def test_api_key_manager_rotates(tmp_path):
    """Test APIKeyManager rotates to next key."""
    # Arrange
    config = tmp_path / "api_keys.json"
    config.write_text(json.dumps({
        "anthropic_keys": ["key1", "key2"],
        "current_key_index": 0
    }))
    mgr = APIKeyManager(config)

    # Act: Rotate
    new_key = mgr.rotate_key()

    # Assert: Rotated to key 2
    assert mgr.current_index == 1
    assert new_key == "key2"

    # Assert: Persisted
    saved = json.loads(config.read_text())
    assert saved["current_key_index"] == 1
```

## Remember

**You are a test WRITER, not a test RUNNER.**

Write good tests, document them, and let the system handle execution.
