> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# R04: Copy Server Modules

## Depends: R01

## Task
Copy all server source files into the new package.

## Steps
```bash
cp packages/csc-server/csc_server/*.py packages/csc-service/csc_service/server/
```

If the source uses `packages/csc-server/*.py` (flat layout without csc_server subdir), copy from there instead:
```bash
# Check which layout exists:
ls packages/csc-server/csc_server/ 2>/dev/null || ls packages/csc-server/*.py
# Copy from whichever location has the .py files
```

Key files to verify exist in destination:
- `server.py` - Main server class
- `server_message_handler.py` - IRC command handlers
- `storage.py` - JSON persistence
- `network.py` - UDP socket handling
- `main.py` - Entry point

## Verification
- `ls packages/csc-service/csc_service/server/server.py` exists
- `ls packages/csc-service/csc_service/server/server_message_handler.py` exists
- `ls packages/csc-service/csc_service/server/main.py` exists
