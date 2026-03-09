---
urgency: P3
description: Convert pm.py state file to use Data class
cost_sensitive: true
---

# Fix: PM State Storage (pm.py)

## Violation Location
- File: `packages/csc-service/csc_service/infra/pm.py:148`
- Pattern: Direct JSON write to project root

## Current Code
```python
STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
```

## Should Be
```python
# In PM class __init__:
self.source_filename = "pm_state.json"
self.connect()

# Instead of STATE_FILE.write_text:
self.put_data("pm_state", state)  # Automatically persists to temp/csc/run/
```

## Implementation Steps
1. Make PM inherit from or use Data class
2. Call self.connect() in __init__ with source_filename
3. Replace STATE_FILE.write_text(json.dumps(...)) with self.put_data()
4. Replace STATE_FILE.read_text() → json.loads() with self.get_data()
5. Verify PM startup and state persistence work

## Why This Matters
- Stores PM runtime state in temp/csc/run/ (not project root)
- Thread-safe persistence
- Single source of truth for PM state

