---
urgency: P3
description: Convert queue_worker.py state files to use Data class
cost_sensitive: true
---

# Fix: Queue-Worker State Storage (queue_worker.py)

## Violation Locations
Multiple raw JSON writes in queue_worker.py:
- Line 458: Agent result JSON dump
- Line 482: Agent state JSON dump  
- Line 512: Stale items JSON dump
- Line 985: Stale state JSON dump

## Pattern
```python
temp_file.write_text(json.dumps(data, indent=4), encoding='utf-8')
```

## Should Use Data Class
Create a QueueWorkerData class (inherits from Data):
```python
class QueueWorkerData(Data):
    def __init__(self):
        super().__init__()
        self.source_filename = "queue_worker_state.json"
        self.connect()

# Usage:
qw_data = QueueWorkerData()
qw_data.put_data("agent_results", data)
qw_data.put_data("agent_state", state)
qw_data.put_data("stale_items", items)
```

## Implementation Steps
1. Create QueueWorkerData class inheriting from Data
2. Initialize with proper source_filename
3. Replace all temp_file.write_text(json.dumps()) with put_data()
4. Replace all open().read() → json.loads() with get_data()
5. Verify queue-worker still tracks jobs properly

## Why This Matters
- Multiple files scattered in project root/temp → single JSON file
- Thread-safe concurrent access to queue state
- Platform-aware directory management

