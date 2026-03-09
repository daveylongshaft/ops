# R17: Rewrite Imports in server/ Modules

## Depends: R04, R15

## Task
Update all import statements in `packages/csc-service/csc_service/server/*.py`
to use the new import paths.

## Rules
In every `.py` file in `packages/csc-service/csc_service/server/`:
- Replace `from csc_shared.` with `from csc_service.shared.`
- Replace `from csc_shared import` with `from csc_service.shared import`
- Replace `import csc_shared.` with `import csc_service.shared.`
- Replace `from csc_server.` with `from csc_service.server.`
- Replace `from csc_server import` with `from csc_service.server import`
- Replace `import csc_server.` with `import csc_service.server.`
- Replace `from csc_client` with `from csc_service.client` (server.py line ~574 imports Client)

## Known Imports to Fix
From the current source:
- `server.py`: `from csc_shared.channel import ChannelManager`, `from csc_shared.chat_buffer import ChatBuffer`, `from csc_shared.irc import SERVER_NAME`, `from csc_shared.crypto import ...`, `from csc_client import Client`
- `server_message_handler.py`: `from csc_shared.irc import (...)`, `from csc_shared.crypto import DHExchange`, inline `from csc_shared.irc import IRCMessage`
- `network.py`: `from csc_shared.platform import Platform`
- `client.py`: `from csc_shared.data import Data`, `from csc_shared.irc import ...`
- `server_s2s.py`: inline `from csc_shared.irc import format_irc_message`, `from csc_shared.irc import SERVER_NAME`
- `server_message_handler.py` line ~941: `from csc_server.service import Service as BaseService`

## Verification
- `grep -r "from csc_shared" packages/csc-service/csc_service/server/` returns nothing
- `grep -r "from csc_server\b" packages/csc-service/csc_service/server/` returns nothing (ignore csc_service.server)
- `grep -r "from csc_client" packages/csc-service/csc_service/server/` returns nothing


DEAD END - csc-service package already consolidated and operational
