> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# R18: Rewrite Imports in client/ Modules

## Depends: R05, R15

## Task
Update all import statements in `packages/csc-service/csc_service/client/*.py`
to use the new import paths.

## Rules
In every `.py` file in `packages/csc-service/csc_service/client/`:
- Replace `from csc_shared.` with `from csc_service.shared.`
- Replace `from csc_client.` with `from csc_service.client.`
- Replace `import csc_shared.` with `import csc_service.shared.`
- Replace `import csc_client.` with `import csc_service.client.`

## Known Imports to Fix
- `client.py`: `from csc_shared.network import Network`, `from csc_shared.data import Data`, `from csc_shared.irc import ...`, `from csc_client.aliases import Aliases`, `from csc_client.macros import Macros`, `from csc_client.client_file_handler import ClientFileHandler`, `from csc_client.client_service_handler import ClientServiceHandler`
- `macros.py`: `from csc_shared.data import Data`, `from csc_shared.log import Log`
- `network.py`: `from csc_shared.version import Version`

## Verification
- `grep -r "from csc_shared" packages/csc-service/csc_service/client/` returns nothing
- `grep -r "from csc_client" packages/csc-service/csc_service/client/` returns nothing
