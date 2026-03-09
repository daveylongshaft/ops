---
urgency: P2
description: Create unified ClientStateData and update all 6 client implementations
cost_sensitive: true
---

# Fix: Unified Client State Management → ClientStateData Class

## Violation Locations
6 client implementations have independent state persistence using raw `open()`:
- Claude: `packages/csc-service/csc_service/clients/claude/claude.py:96,112`
- Gemini: `packages/csc-service/csc_service/clients/gemini/gemini.py:126,142`
- ChatGPT: `packages/csc-service/csc_service/clients/chatgpt/chatgpt.py:62,98,114`
- DMRBot: `packages/csc-service/csc_service/clients/dmrbot/dmrbot.py:88,100`
- Client (CLI): `packages/csc-service/csc_service/client/client.py:142,158,319`
- Bridge: `packages/csc-service/csc_service/bridge/main.py:193` (config only)

## Current Issue
Each client manages its own state file independently without using Data class:

```python
# Claude example (similar in all 6 clients)
temp_file = self.state_file.with_suffix('.json.tmp')
with open(temp_file, 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2)
temp_file.replace(self.state_file)

with open(self.state_file, 'r', encoding='utf-8') as f:
    state = json.load(f)
```

## Should Be
Create unified ClientStateData class and use in all clients:

```python
# New file: packages/csc-service/csc_service/shared/client_state.py
from csc_service.shared.data import Data

class ClientStateData(Data):
    def __init__(self, client_name):
        super().__init__()
        self.source_filename = f"{client_name}_state.json"
        self.client_name = client_name
        self.connect()

# Usage in each client:
class Claude(Client):
    def __init__(self):
        super().__init__("claude_config.json", host=host, port=server_port)
        self.state_data = ClientStateData("claude")
        # ... rest of init ...
    
    def _save_client_state(self):
        state = {
            "nick": self.name,
            "modes": self.user_modes,
            "channels": list(self.joined_channels)
        }
        self.state_data.put_data("state", state)
    
    def _load_client_state(self):
        return self.state_data.get_data("state")
```

## Implementation Steps
1. Create `packages/csc-service/csc_service/shared/client_state.py` with ClientStateData class
2. Update 6 client implementations to use ClientStateData:
   - Claude: Replace lines 96, 112 with state_data methods
   - Gemini: Replace lines 126, 142
   - ChatGPT: Replace lines 62, 98, 114
   - DMRBot: Replace lines 88, 100
   - Client: Replace lines 142, 158, 319
   - Bridge: Replace line 193 with config_data
3. Remove raw file handling code from each client
4. Test state persistence across restarts for each client

## Why This Matters
- Consolidates 6+ independent implementations into one unified class
- All client state stored in temp/csc/run/ (not scattered in multiple locations)
- Thread-safe persistence with consistent error handling
- Easier to modify client state behavior going forward
- Reduces code duplication and maintenance burden

## Acceptance Criteria
✓ ClientStateData class created and inherits from Data
✓ All 6 clients updated to use ClientStateData
✓ State files stored in temp/csc/run/ (not scattered)
✓ Each client's state persists correctly across restarts
✓ No breaking changes to client APIs
✓ All client tests pass
