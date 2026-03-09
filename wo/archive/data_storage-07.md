---
urgency: P3
description: Fix NickservService user registration DB to use Data class
cost_sensitive: true
---

# Fix: NickservService User DB → Data Class

## Violation Location
`packages/csc-service/csc_service/shared/services/nickserv_service.py:55,77`

## Current Issue
NickservService stores user registration in `csc_service/server/nickserv.db` using raw `open()`:

```python
# Line 55: Reading
with open(self.db_file, 'r', encoding='utf-8') as f:
    for line in f:
        # parse user registration

# Line 77: Writing
with open(self.db_file, 'w', encoding='utf-8') as f:
    for nick_lower, data in sorted(self._registry.items()):
        line = f"{data['nick']}:{data['pass_hash']}:{data['email']}:{data['registered_timestamp']}\n"
        f.write(line)
```

## Should Be
Use Data class for persistent user registration:

```python
from csc_service.shared.data import Data

class NickservData(Data):
    def __init__(self):
        super().__init__()
        self.source_filename = "nickserv_users.json"
        self.connect()

class Nickserv(Service):
    def __init__(self, server_instance):
        super().__init__(server_instance)
        self.name = "nickserv"
        self.init_data()
        self.user_data = NickservData()
        self._registry = {}
        self._load_db()
    
    def _load_db(self):
        users = self.user_data.get_data("users") or {}
        self._registry = {}
        for nick_lower, user_info in users.items():
            self._registry[nick_lower] = user_info
    
    def _save_db(self):
        # Store registry back to Data class
        self.user_data.put_data("users", self._registry)
```

## Implementation Steps
1. Create NickservData class inheriting from Data
2. Modify Nickserv.__init__() to instantiate NickservData
3. Update _load_db() to use self.user_data.get_data()
4. Update _save_db() to use self.user_data.put_data()
5. Convert text file format (nick:hash:email:timestamp) to JSON dict
6. Handle migration from old nickserv.db to new JSON format
7. Test user registration persists across restarts

## Migration Strategy
- Check if old nickserv.db exists
- If exists: parse it and migrate to Data class
- If not: start fresh with empty user registry
- No breaking changes to Nickserv API

## Why This Matters
- User registration data moves from `csc_service/server/` to temp/csc/run/
- Thread-safe persistence with Data class locking
- JSON format more flexible than text file
- Aligns with framework architecture

## Acceptance Criteria
✓ NickservData class created and inherits from Data
✓ nickserv_users.json stored in temp/csc/run/
✓ User registration persists correctly across restarts
✓ Old nickserv.db migrated to new JSON format
✓ No breaking changes to Nickserv API
✓ Tests pass for user registration functionality
