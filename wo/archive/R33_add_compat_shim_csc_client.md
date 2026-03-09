> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# R33: Add Backward-Compat Shim for csc_client

## Depends: R18

## Task
Add a compatibility shim so that `import csc_client` still works.

## Steps
1. Create `packages/csc-service/csc_client/__init__.py`:
```python
"""Backward-compatibility shim: csc_client -> csc_service.client"""
from csc_service import client as _client
import sys
sys.modules[__name__] = _client
```

2. Make sure `csc_client` is included in pyproject.toml packages:
```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["csc_service*", "csc_shared*", "csc_server*", "csc_client*"]
```

## Verification
- `pip install -e packages/csc-service`
- `python -c "from csc_client.client import Client; print('OK')"` works
