# Q05: Documentation, Migration & Cleanup

## Objective

Complete migration from batch/bash scripts to pure Python, with comprehensive documentation and cleanup.

## Documentation to Create

### QUEUE_WORKER_ARCHITECTURE.md

High-level system design document covering:
- Overview and workflow
- Directory structure
- Processing flow (detailed sequence)
- One-at-a-time enforcement
- Cross-platform support
- WIP journaling
- Error handling
- Architecture rationale
- Performance characteristics
- Monitoring guidelines

### MIGRATION_GUIDE.md

Step-by-step migration instructions:
- Overview and impact summary
- Migration checklist (3 phases)
- Backward compatibility notes
- Testing procedures (manual tests)
- Troubleshooting guide
- Rollback procedures
- Post-migration monitoring

### bin/SCRIPTS.md

Documentation for all bin/ scripts:
- queue-worker
- run_agent.py
- agent (existing)

## Files to Update

### README.md

Add section explaining:
- New queue-based workflow
- Unchanged API (agent assign still works)
- Where to find more details

### agents/<name>/context/README.md

Add notes on:
- Queue integration
- Workflow steps
- Agent journaling requirements

## Cleanup Tasks

### Remove from Version Control

- `agents/*/bin/run_agent.sh`
- `agents/*/bin/run_agent.bat`

### Create Migration Script

`bin/migrate-to-python-queue.sh`:
- Verify new code in place
- Stop old queue-worker
- Remove old scripts
- Create queue directories
- Test new queue-worker
- Start new queue-worker

## Acceptance Criteria

- ✅ QUEUE_WORKER_ARCHITECTURE.md complete and clear
- ✅ MIGRATION_GUIDE.md with step-by-step instructions
- ✅ All references to old scripts removed
- ✅ Migration script created and tested
- ✅ Old batch/bash files removed from git
- ✅ README.md updated with queue info
- ✅ Team documentation reviewed

## Dependencies

- Requires Q01, Q02, Q03, Q04 implementations
- Blocks: nothing (final phase)


DEAD END - Queue worker implemented, docs superseded by current system
