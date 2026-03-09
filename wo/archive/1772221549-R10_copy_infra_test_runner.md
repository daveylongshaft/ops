# R10: Copy test-runner Into infra/

## Depends: R01

## Task
Copy the test-runner script into `csc_service/infra/` as a Python module.

## Steps
1. Copy `bin/test-runner` to `packages/csc-service/csc_service/infra/test_runner.py`
2. The file is already Python (despite no `.py` extension). Just copy it.

```bash
cp bin/test-runner packages/csc-service/csc_service/infra/test_runner.py
```

## Verification
- `ls packages/csc-service/csc_service/infra/test_runner.py` exists
- `head -1 packages/csc-service/csc_service/infra/test_runner.py` shows `#!/usr/bin/env python3` or similar


DEAD END - csc-service package already consolidated and operational
