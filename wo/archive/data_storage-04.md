---
urgency: P2
description: Fix PersistentClientManager to use Data class
cost_sensitive: true
---

# Fix: PersistentClientManager Raw File I/O → Data Class

## Violation Location
`packages/csc-service/csc_service/server/persistent_clients.py:65,82,116,124`

## Current Issue
PersistentClientManager manages client session state using raw `open()` to `/opt/csc/server/active_clients.json`:

```python
# Line 65, 124: Writing
with open(temp_path, 'w') as f:
    json.dump(data, f, indent=2)

# Line 82, 116: Reading
with open(self.filepath, 'r') as f:
    data = json.load(f)
```

## Should Be
Use Data class for thread-safe persistence in temp/csc/run/:

```python
from csc_service.shared.data import Data

class PersistentClientData(Data):
    def __init__(self):
        super().__init__()
        self.source_filename = "persistent_clients.json"
        self.connect()

class PersistentClientManager:
    def __init__(self, timeout=120):
        self.data = PersistentClientData()
        self.timeout = timeout

    def save_clients(self, clients_dict, registration_state):
        data = {}
        for addr, info in clients_dict.items():
            # ... build data dict ...
            data[key] = {...}
        
        # Use Data class instead of temp file + rename
        self.data.put_data("active_clients", data)

    def load_clients(self):
        data = self.data.get_data("active_clients") or {}
        
        now = time.time()
        active_clients = {}
        
        for key, info in data.items():
            # ... filter expired clients ...
            if now - self.timeout <= info.get("last_seen", 0):
                addr = self._key_to_addr(key)
                active_clients[addr] = info
        
        return active_clients
```

## Implementation Steps
1. Create PersistentClientData class inheriting from Data
2. Modify PersistentClientManager.__init__() to instantiate PersistentClientData
3. Replace save_clients() to use self.data.put_data()
4. Replace load_clients() to use self.data.get_data()
5. Remove temp file path logic and atomic rename (Data class handles this)
6. Test server restart with active clients

## Why This Matters
- Moves client session state from `/opt/csc/server/` to temp/csc/run/
- Thread-safe persistence via Data class locking
- Server recovery and session persistence unified
- Eliminates hardcoded paths

## Acceptance Criteria
✓ PersistentClientManager uses Data class for all persistence
✓ persistent_clients.json stored in temp/csc/run/ (not /opt/csc/server/)
✓ Client session recovery works across restarts
✓ Concurrent access thread-safe via Data class lock
✓ Tests pass for session recovery
