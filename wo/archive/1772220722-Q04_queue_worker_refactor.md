---
requires: ["python3", "git"]
platform: ["windows", "linux", "macos"]
agent: opus
depends_on: ["Q02", "Q03"]
---

# Q04: Queue Worker Service Refactoring - Pure Python Implementation

## Goal

Refactor queue_worker_service.py to use pure Python RunAgentExecutor instead of spawning shell scripts.

## Tasks

1. **Import and Use RunAgentExecutor**
   - Import RunAgentExecutor class
   - In cycle() method: replace script spawning with executor

2. **Refactor Queue Processing Cycle**
   - Scan agents/*/queue/in/ for workorders
   - Move queue/in/ to queue/work/
   - Create RunAgentExecutor and execute
   - On success: move queue/work/ to queue/out/, move WIP to done/
   - On failure: move WIP to ready/ for retry

3. **Remove Shell Path Conversion**
   - Delete _get_path_for_shell() method
   - Remove all shell=True subprocess handling for paths
   - Paths handled by RunAgentExecutor

4. **Enhance Metadata Tracking**
   - Store PID in metadata JSON
   - Use for detecting stale processes

5. **Improve Error Handling**
   - Increment retry counter on failure
   - Move to hold/ after 3 retries

## Files to Modify

- packages/csc-service/csc_service/shared/services/queue_worker_service.py
  - Remove _get_path_for_shell()
  - Refactor cycle() method
  - Update process tracking

## Acceptance Criteria

- [x] Uses RunAgentExecutor instead of shell scripts
- [x] Path conversion logic removed
- [x] Process tracking via metadata JSON
- [x] Error handling covers main cases
- [x] Queue operations atomic

## Dependencies

- Depends on: Q02, Q03
- Enables: Q05


## Work Log
START 2026-02-26 - Opus designing pure Python queue system


--- AUDIT [2026-02-27 13:22] ---
INCOMPLETE
Pending:
  - Import RunAgentExecutor and integrate into queue_worker_service.py
  - Refactor cycle() method to replace script spawning
  - Implement queue folder transitions (in/ → work/ → out/, or work/ → ready/)
  - Remove _get_path_for_shell() method
  - Implement metadata JSON storage with PID tracking
  - Implement retry counter and hold/ folder logic after 3 failures
  - Testing of queue operations and error handling
  - Verification that work log shows completed implementation steps
Work log only shows design phase start; no implementation, testing, or completion marker present


DEAD END - Superseded by current queue_worker.py and run_agent.py implementation
