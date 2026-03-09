> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

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
