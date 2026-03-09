> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# R32: Add Backward-Compat Shim for csc_server

## Depends: R17

## Task
Add a compatibility shim so that `import csc_server` still works.

## Steps
1. Create `packages/csc-service/csc_server/__init__.py`:
```python
"""Backward-compatibility shim: csc_server -> csc_service.server"""
from csc_service import server as _server
import sys
sys.modules[__name__] = _server
```

2. Make sure `csc_server` is included in pyproject.toml packages:
```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["csc_service*", "csc_shared*", "csc_server*"]
```

## Verification
- `pip install -e packages/csc-service`
- `python -c "from csc_server.server import Server; print('OK')"` works
