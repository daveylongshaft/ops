# R09: Copy Bridge Modules

## Depends: R01

## Task
Copy IRC bridge proxy files into the new package.

## Steps
```bash
ls packages/csc-bridge/csc_bridge/ 2>/dev/null || ls packages/csc-bridge/*.py
cp packages/csc-bridge/csc_bridge/*.py packages/csc-service/csc_service/bridge/ 2>/dev/null || \
cp packages/csc-bridge/*.py packages/csc-service/csc_service/bridge/
```

Key files:
- `bridge.py` - Main bridge implementation
- `data_bridge.py` - Data bridge layer
- `main.py` - Entry point

## Verification
- `ls packages/csc-service/csc_service/bridge/bridge.py` exists


DEAD END - csc-service package already consolidated and operational
