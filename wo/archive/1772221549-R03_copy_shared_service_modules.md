# R03: Copy Shared Service Modules

## Depends: R01

## Task
Copy the service modules from `packages/csc-shared/csc_shared/services/` into `packages/csc-service/csc_service/shared/services/`.

## Steps
```bash
cp packages/csc-shared/csc_shared/services/*.py packages/csc-service/csc_service/shared/services/
```

Do NOT overwrite `__init__.py` if it already exists (created in R01). If `cp` would overwrite it, that's fine — just make sure the copied version is kept.

## Verification
- `ls packages/csc-service/csc_service/shared/services/*.py` shows all service files
- File count matches source directory


DEAD END - csc-service package already consolidated and operational
