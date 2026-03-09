> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# Rename queue-worker to queue throughout codebase

## Objective
Rename 'queue-worker' service to 'queue' everywhere for consistency and shorter naming.

## Files to Update
Search for 'queue-worker' and replace with 'queue' in:
- packages/csc-service/csc_service/cli/csc_ctl.py - service name in subparsers
- packages/csc-service/csc_service/config.py - service definitions
- packages/csc-service/csc_service/main.py - service initialization
- packages/csc-service/csc_service/infra/queue_worker.py - docstrings, KNOWN_AGENTS
- csc-service.json - service name entries
- CLAUDE.md - documentation references
- Any bin/ scripts that reference queue-worker

## Important Notes
- Keep filenames as queue_worker.py (underscores) - only rename service/display name
- Update help text, log messages, docstrings
- Update service registration and config keys
- Verify 'csc-ctl status' shows 'queue' instead of 'queue-worker'
- Verify 'csc-ctl run queue' works after changes

## Verification Steps
1. csc-ctl status should show 'queue' in service list
2. csc-ctl run queue should execute successfully
3. All help text and logs reference 'queue'
4. grep for 'queue-worker' - should only appear in file paths, not service names

## Commit Message
refactor: Rename queue-worker service to queue for consistency
