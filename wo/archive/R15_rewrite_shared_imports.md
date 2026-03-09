> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# R15: Rewrite Imports in shared/ Modules

## Depends: R02

## Task
Update all import statements in `packages/csc-service/csc_service/shared/*.py`
to use the new `csc_service.shared` import path instead of `csc_shared`.

## Rules
In every `.py` file in `packages/csc-service/csc_service/shared/`:
- Replace `from csc_shared.` with `from csc_service.shared.`
- Replace `from csc_shared import` with `from csc_service.shared import`
- Replace `import csc_shared.` with `import csc_service.shared.`
- Leave `from .` relative imports unchanged (they still work)

## Example
```python
# BEFORE:
from csc_shared.irc import IRCMessage
from csc_shared.channel import Channel
import csc_shared.platform

# AFTER:
from csc_service.shared.irc import IRCMessage
from csc_service.shared.channel import Channel
import csc_service.shared.platform
```

## Verification
- `cd packages/csc-service && pip install -e .`
- `python -c "from csc_service.shared.irc import IRCMessage; print('OK')"`
- `grep -r "from csc_shared" packages/csc-service/csc_service/shared/` returns nothing
