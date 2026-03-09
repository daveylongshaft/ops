# R16: Rewrite Imports in shared/services/ Modules

## Depends: R03, R15

## Task
Update all import statements in `packages/csc-service/csc_service/shared/services/*.py`
to use the new `csc_service.shared` import path.

## Rules
In every `.py` file in `packages/csc-service/csc_service/shared/services/`:
- Replace `from csc_shared.` with `from csc_service.shared.`
- Replace `from csc_shared import` with `from csc_service.shared import`
- Replace `import csc_shared.` with `import csc_service.shared.`
- Replace `from csc_server.` with `from csc_service.server.`
- Leave `from .` relative imports unchanged

## Special Case
The file `wakeword_service.py` imports `from csc_server.service import Service`. Change to:
```python
from csc_service.server.service import Service
```

## Verification
- `grep -r "from csc_shared" packages/csc-service/csc_service/shared/services/` returns nothing
- `grep -r "from csc_server" packages/csc-service/csc_service/shared/services/` returns nothing


DEAD END - csc-service package already consolidated and operational
