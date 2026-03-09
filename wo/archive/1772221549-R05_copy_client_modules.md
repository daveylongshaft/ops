# R05: Copy Client (Human CLI) Modules

## Depends: R01

## Task
Copy human CLI client files into the new package.

## Steps
```bash
# Check layout
ls packages/csc-client/csc_client/ 2>/dev/null || ls packages/csc-client/*.py
# Copy .py files to destination
cp packages/csc-client/csc_client/*.py packages/csc-service/csc_service/client/ 2>/dev/null || \
cp packages/csc-client/*.py packages/csc-service/csc_service/client/
```

Key files to verify:
- `client.py` - Main Client class
- `main.py` - Entry point
- `macros.py` - Macro support
- `aliases.py` - Alias handling (if exists)
- `network.py` - Client network layer (if exists)

## Verification
- `ls packages/csc-service/csc_service/client/client.py` exists
- `ls packages/csc-service/csc_service/client/main.py` exists


DEAD END - csc-service package already consolidated and operational
