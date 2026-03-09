> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# R21: Rewrite Imports in clients/chatgpt/

## Depends: R08, R15, R18

## Task
Update all import statements in `packages/csc-service/csc_service/clients/chatgpt/*.py`
to use the new import paths.

## Rules
- Replace `from csc_shared.` with `from csc_service.shared.`
- Replace `from csc_client.` with `from csc_service.client.`

## Known Imports to Fix
- `chatgpt.py`: `from csc_shared.secret import get_claude_api_key, get_claude_oper_credentials` → `from csc_service.shared.secret import ...`
- `chatgpt.py`: `from csc_shared.irc import parse_irc_message, format_irc_message, SERVER_NAME` → `from csc_service.shared.irc import ...`
- `chatgpt.py`: `from csc_client.client import Client` → `from csc_service.client.client import Client`

## Verification
- `grep -r "from csc_shared\|from csc_client" packages/csc-service/csc_service/clients/chatgpt/` returns nothing
