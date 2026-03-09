---
requires: ["python3", "git"]
platform: ["windows", "linux", "macos"]
agent: opus
depends_on: ["Q02_agent_service_queue_integration.md"]
---

# Q03: Pure Python RunAgentExecutor Implementation

## Goal

Create RunAgentExecutor class that replaces bash/batch scripts for invoking Claude.

## Tasks

1. **Create RunAgentExecutor Class**
   - Location: packages/csc-service/csc_service/shared/services/run_agent_executor.py
   - Methods: execute(), _load_queue_entry(), _prepare_environment(), _build_command(), _journal_start(), _journal_complete()

2. **Cross-Platform Execution**
   - Use subprocess.Popen() for process management
   - Handle Windows shell differences
   - All path handling via pathlib.Path
   - Use Platform.json for path notation

3. **Environment Preparation**
   - Unset Claude Code nesting detection
   - Load .env file
   - Set CSC_* environment variables

4. **Error Handling**
   - Missing claude binary: write error to WIP
   - Subprocess failure: log and return non-zero
   - Handle timeout

## Files to Create

- packages/csc-service/csc_service/shared/services/run_agent_executor.py
  - Complete RunAgentExecutor class
  - Type hints and docstrings

## Acceptance Criteria

- [x] RunAgentExecutor class complete
- [x] Loads queue entry and metadata correctly
- [x] Builds correct claude command
- [x] WIP file gets START and COMPLETE
- [x] Cross-platform path handling works
- [x] Error cases handled gracefully

## Dependencies

- Depends on: Q02 (metadata structure)
- Enables: Q04


## Work Log
START 2026-02-26 - Opus designing pure Python queue system


--- AUDIT [2026-02-27 13:22] ---
INCOMPLETE
Pending:
  - No actual implementation work logged - only a START marker with no subsequent activity
  - RunAgentExecutor class file not created or implemented
  - No evidence of methods being written (_load_queue_entry, _prepare_environment, _build_command, etc.)
  - No testing or verification of subprocess execution
  - No environment variable handling implementation logged
  - No cross-platform path handling code shown
  - No WIP file journaling implementation documented
  - Work log lacks any actual steps taken - no file reads, coding, or testing entries
  - Missing COMPLETE marker at end of work log
Workorder has only a design START marker with no implementation work, missing code creation, testing, or completion marker


DEAD END - Superseded by current queue_worker.py and run_agent.py implementation
