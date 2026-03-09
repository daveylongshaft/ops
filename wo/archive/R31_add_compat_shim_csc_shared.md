> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# R31: Add Backward-Compat Shim for csc_shared

## Depends: R15

## Task
Add a compatibility shim so that `import csc_shared` still works after
installing csc-service. This prevents breaking existing tests and old packages
during the transition.

## Steps
1. Create `packages/csc-service/csc_shared/__init__.py`:
```python
"""Backward-compatibility shim: csc_shared -> csc_service.shared"""
from csc_service.shared import *
from csc_service import shared as _shared
import sys
sys.modules[__name__] = _shared
```

2. Add `csc_shared` to the packages list in `pyproject.toml`:
```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["csc_service*", "csc_shared*"]
```

## Why
Tests and old packages still use `from csc_shared.irc import ...`. This shim
lets them work without modification. It can be removed once all imports are
migrated.

## Verification
- `pip install -e packages/csc-service`
- `python -c "from csc_shared.irc import IRCMessage; print('OK')"` works
- `python -c "from csc_service.shared.irc import IRCMessage; print('OK')"` also works
