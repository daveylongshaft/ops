---
urgency: P2
description: Fix APIKeyManager to use Data class for persistent state
cost_sensitive: true
---

# Fix: APIKeyManager Raw File I/O → Data Class

## Violation Location
`packages/csc-service/csc_service/shared/api_key_manager.py:55,80,87`

## Current Issue
APIKeyManager reads/writes `api_keys.json` from project root using raw `open()`:

```python
# Lines 55, 80: Reading
with open(self.config_path, 'r') as f:
    config = json.load(f)

# Line 87: Writing
with open(self.config_path, 'w') as f:
    json.dump(config, f, indent=2)
```

## Should Be
Use Data class for persistent state management in temp/csc/run/:

```python
from csc_service.shared.data import Data

class APIKeyData(Data):
    def __init__(self):
        super().__init__()
        self.source_filename = "api_keys.json"
        self.connect()

class APIKeyManager:
    def __init__(self, config_path=None):
        self.data = APIKeyData()
        self.keys = []
        self.current_index = 0
        self.load_config()

    def load_config(self):
        config = self.data.get_data("api_keys_config")
        if config:
            self.keys = config.get("keys", [])
            self.current_index = config.get("current_key_index", 0)
        else:
            # Fallback to environment variable
            env_key = os.getenv("ANTHROPIC_API_KEY")
            if env_key:
                self.keys = [env_key]
                self.current_index = 0

    def save_config(self):
        self.data.put_data("api_keys_config", {
            "keys": self.keys,
            "current_key_index": self.current_index
        })
```

## Implementation Steps
1. Create APIKeyData class inheriting from Data
2. Modify APIKeyManager.__init__() to instantiate APIKeyData
3. Replace load_config() to use self.data.get_data()
4. Replace save_config() to use self.data.put_data()
5. Remove hardcoded config_path parameter (or make it optional for testing)
6. Verify API key rotation works with new storage

## Why This Matters
- Moves API key state from project root to temp/csc/run/
- Thread-safe persistence via Data class locking
- Single source of truth for key rotation state
- Aligns with framework architecture

## Acceptance Criteria
✓ APIKeyManager inherits behavior from Data class
✓ api_keys.json stored in temp/csc/run/ (not project root)
✓ API key rotation persists correctly
✓ Fallback to environment variable still works
✓ No breaking changes to existing API
