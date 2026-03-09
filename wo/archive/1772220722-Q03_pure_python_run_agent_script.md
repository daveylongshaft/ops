# Q03: Pure Python `run_agent.py` Script

## Objective

Replace batch/bash scripts with a single pure Python `run_agent.py` that handles agent execution across all platforms.

## Current Architecture

- `agents/<name>/bin/run_agent.sh` (bash) and `run_agent.bat` (batch) co-exist
- Each must handle platform-specific path conversions
- Difficult to maintain synchronization between versions

## New Architecture

Single `run_agent.py` script that:
1. Reads workorder from queue/work/
2. Unsets CLAUDE_CODE_NESTING_DEPTH
3. Spawns claude command with platform-correct paths
4. Journals to WIP file
5. Marks COMPLETE when done
6. Works on Windows/Linux/macOS/Android

## Files to Create/Modify

### Create: `bin/run_agent.py`

**Main Flow**:
- Initialize AgentRunner(workorder_path)
- Read and extract prompt
- Setup environment (unset nesting detection)
- Build and run claude CLI command
- Journal progress
- Check WIP for COMPLETE
- Return appropriate exit code

### Delete from git:
- `agents/*/bin/run_agent.sh`
- `agents/*/bin/run_agent.bat`

## Acceptance Criteria

- ✅ Single script works on Windows/Linux/macOS
- ✅ Reads workorder from queue/work/
- ✅ Unsets CLAUDE_CODE_NESTING_DEPTH
- ✅ Initializes WIP file with timestamp and PID
- ✅ Detects COMPLETE in WIP file
- ✅ Uses pathlib for all paths
- ✅ Returns exit code: 0 if complete, 1 if incomplete

## Dependencies

- Requires Q01 (workorder structure)
- Requires Q02 (queue_worker integration)
- Does NOT depend on Q04-Q05


--- AUDIT [2026-02-27 13:22] ---
INCOMPLETE
Pending:
  - No Work Log section present - file contains only objective, architecture, and acceptance criteria
  - No agent activity logged showing implementation steps
  - No COMPLETE marker indicating work was finished
  - No evidence of actual script creation (bin/run_agent.py implementation not shown)
  - No test results or verification that the script works on multiple platforms
  - No confirmation that bash/batch files were deleted from git
  - No demonstration of WIP file journaling functionality
  - No proof that CLAUDE_CODE_NESTING_DEPTH environment variable handling was implemented
This is a planning/specification document only - no implementation work log or completion evidence provided


DEAD END - Superseded by current queue_worker.py and run_agent.py implementation
