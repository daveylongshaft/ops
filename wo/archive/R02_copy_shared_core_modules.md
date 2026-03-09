> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# R02: Copy Shared Core Modules

## Depends: R01

## Task
Copy the core shared library files from `packages/csc-shared/csc_shared/` into `packages/csc-service/csc_service/shared/`.

## Steps
Copy these files (preserve content exactly):
```
packages/csc-shared/csc_shared/irc.py       → packages/csc-service/csc_service/shared/irc.py
packages/csc-shared/csc_shared/channel.py   → packages/csc-service/csc_service/shared/channel.py
packages/csc-shared/csc_shared/user.py      → packages/csc-service/csc_service/shared/user.py
packages/csc-shared/csc_shared/logging.py   → packages/csc-service/csc_service/shared/logging.py
packages/csc-shared/csc_shared/platform.py  → packages/csc-service/csc_service/shared/platform.py
packages/csc-shared/csc_shared/crypto.py    → packages/csc-service/csc_service/shared/crypto.py
packages/csc-shared/csc_shared/secret.py    → packages/csc-service/csc_service/shared/secret.py
packages/csc-shared/csc_shared/network.py   → packages/csc-service/csc_service/shared/network.py
packages/csc-shared/csc_shared/data.py      → packages/csc-service/csc_service/shared/data.py
packages/csc-shared/csc_shared/log.py       → packages/csc-service/csc_service/shared/log.py
packages/csc-shared/csc_shared/version.py   → packages/csc-service/csc_service/shared/version.py
packages/csc-shared/csc_shared/chat_buffer.py → packages/csc-service/csc_service/shared/chat_buffer.py
packages/csc-shared/csc_shared/utils.py     → packages/csc-service/csc_service/shared/utils.py
```

Also copy any other `.py` files in `packages/csc-shared/csc_shared/` that are NOT in a subdirectory. Use:
```bash
cp packages/csc-shared/csc_shared/*.py packages/csc-service/csc_service/shared/
```

Do NOT copy `__init__.py` (it was already created in R01).

## Verification
- `ls packages/csc-service/csc_service/shared/irc.py` exists
- `ls packages/csc-service/csc_service/shared/platform.py` exists
- File count matches: same number of `.py` files in both directories (minus __init__.py)
