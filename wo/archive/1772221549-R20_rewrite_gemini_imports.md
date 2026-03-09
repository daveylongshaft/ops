# R20: Rewrite Imports in clients/gemini/

## Depends: R07, R15, R18

## Task
Update all import statements in `packages/csc-service/csc_service/clients/gemini/*.py`
to use the new import paths.

## Rules
- Replace `from csc_shared.` with `from csc_service.shared.`
- Replace `from csc_client.` with `from csc_service.client.`

## Known Imports to Fix
- `client.py`: `from csc_shared.network import Network`, `from csc_shared.data import Data`, `from csc_shared.irc import ...`
- `gemini.py`: `from csc_shared.irc import parse_irc_message, format_irc_message, SERVER_NAME`
- `macros.py`: `from csc_shared.data import Data`, `from csc_shared.log import Log`

## Verification
- `grep -r "from csc_shared\|from csc_client" packages/csc-service/csc_service/clients/gemini/` returns nothing


DEAD END - csc-service package already consolidated and operational
