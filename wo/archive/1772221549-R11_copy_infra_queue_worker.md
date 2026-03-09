# R11: Copy queue-worker Into infra/

## Depends: R01

## Task
Copy the queue-worker script into `csc_service/infra/` as a Python module.

## Steps
1. Copy `bin/queue-worker` to `packages/csc-service/csc_service/infra/queue_worker.py`
2. The file is already Python (despite no `.py` extension). Just copy it.

```bash
cp bin/queue-worker packages/csc-service/csc_service/infra/queue_worker.py
```

## Verification
- `ls packages/csc-service/csc_service/infra/queue_worker.py` exists


DEAD END - csc-service package already consolidated and operational
