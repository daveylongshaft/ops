> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# R06: Copy Claude AI Client

## Depends: R01

## Task
Copy Claude AI client files into the new package.

## Steps
```bash
ls packages/csc-claude/csc_claude/ 2>/dev/null || ls packages/csc-claude/*.py
cp packages/csc-claude/csc_claude/*.py packages/csc-service/csc_service/clients/claude/ 2>/dev/null || \
cp packages/csc-claude/*.py packages/csc-service/csc_service/clients/claude/
```

Key files:
- `claude.py` - Claude client implementation
- `main.py` - Entry point

## Verification
- `ls packages/csc-service/csc_service/clients/claude/claude.py` exists
