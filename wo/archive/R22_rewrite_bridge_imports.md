> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# R22: Rewrite Imports in bridge/

## Depends: R09, R15

## Task
Update all import statements in `packages/csc-service/csc_service/bridge/*.py`
to use the new import paths.

## Rules
- Replace `from csc_shared.` with `from csc_service.shared.`

## Known Imports to Fix
- `data_bridge.py`: `from csc_shared.data import Data` → `from csc_service.shared.data import Data`
- `bridge.py`: `from csc_shared.crypto import DHExchange, encrypt, decrypt, is_encrypted` → `from csc_service.shared.crypto import ...`

## Verification
- `grep -r "from csc_shared" packages/csc-service/csc_service/bridge/` returns nothing
