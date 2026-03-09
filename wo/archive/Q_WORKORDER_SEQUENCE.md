> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# Pure Python Queue Implementation - Workorder Sequence

## Complete Ordering (Q01-Q06)

All 6 workorders are in `workorders/ready/`. Follow this sequence:

### Phase 1: Analysis & Design

**Q01_core_agent_service_queue_integration.md** (~2 hours)
- Analyze current architecture
- Design pure Python replacement
- Create SYSTEM_DESIGN.md and PYTHON_DESIGN.md
- Identify key modules and files

### Phase 2: Core Implementation

**Q02_python_queue_worker_implementation.md** (~6 hours)
- Create RunAgentExecutor class
- Create WIPJournalHelper class
- Cross-platform process execution
- Safe WIP file journaling

**Q03_pure_python_run_agent_script.md** (~4 hours)
- Create bin/run_agent.py entry point
- Create run_agent.sh and run_agent.bat wrappers
- Argument parsing and exit codes
- Journaling and COMPLETE detection

**Q04_comprehensive_unit_and_integration_tests.md** (~4 hours)
- Update queue_worker_service to use bin/run_agent.py
- Simplify spawn_agent() method
- Remove platform-specific script discovery
- Update process tracking

### Phase 3: Testing

**Q05_integration_testing_and_verification.md** (or Q05_documentation_migration_and_cleanup.md) (~15 hours)
- Create integration test suite
- Test full workflow (assign→queue→done)
- Cross-platform process handling
- Error scenarios and edge cases
- Aim for >85% code coverage

### Phase 4: Documentation

**Q06_documentation_and_finalization.md** (or Q06_documentation_and_cleanup.md) (~5 hours)
- Create QUEUE_SYSTEM.md (complete guide)
- Create MIGRATION.md (upgrade instructions)
- Create OPTIMIZATIONS.md (future improvements)
- Update docstrings and code comments
- Final verification checklist

## Total Effort

- Q01: ~2 hours (Analysis)
- Q02: ~6 hours (Core - Executor)
- Q03: ~4 hours (Core - Script)
- Q04: ~4 hours (Core - Integration)
- Q05: ~15 hours (Testing)
- Q06: ~5 hours (Documentation)

**Total: ~40-50 hours**

## How to Begin

1. Start with Q01 (analysis & design)
2. Follow the sequence Q02→Q03→Q04→Q05→Q06
3. Each workorder enables the next (dependency chain)
4. After Q04, testing and documentation can be parallelized

## Success Criteria

After all 6 workorders:
- Pure Python implementation complete (no bash/batch)
- Cross-platform support verified (Windows/Linux/macOS)
- Full test coverage (>85%)
- Complete documentation (user, developer, migration)
- Ready for production deployment

---

Generated: 2026-02-26
