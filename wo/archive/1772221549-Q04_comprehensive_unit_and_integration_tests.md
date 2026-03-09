# Q04: Comprehensive Unit & Integration Tests

## Objective

Write comprehensive test suite for Q01-Q03 implementations, covering all platforms and error cases.

## Test Scope

Tests for:
1. **Q01 - Agent Service Queue Integration**
2. **Q02 - Queue Worker Implementation**
3. **Q03 - Run Agent Python Script**

## Test Files to Create

### New: `packages/csc-service/tests/test_agent_service_queue.py`

Tests for `agent_service.assign()` queue integration:
- test_assign_creates_queue_in_file()
- test_assign_preserves_front_matter()
- test_assign_creates_queue_directories()
- test_assign_generates_unique_names()
- test_assign_cross_platform_paths()
- test_assign_handles_missing_prompt_file()
- test_assign_handles_readonly_queue_dir()

### New: `packages/csc-service/tests/test_queue_worker.py`

Tests for queue processing logic:
- test_process_queue_in_moves_to_work()
- test_process_queue_in_respects_one_at_a_time()
- test_process_queue_work_detects_completed_agent()
- test_process_queue_work_checks_wip_complete()
- test_process_queue_work_moves_incomplete_to_ready()
- test_spawn_agent_windows_process_group()
- test_spawn_agent_unix_session()
- test_process_alive_windows_tasklist()
- test_process_alive_unix_kill_signal()
- test_git_commit_retry_on_push_failure()

### New: `bin/tests/test_run_agent.py`

Tests for `run_agent.py` script:
- test_run_agent_reads_workorder()
- test_run_agent_extracts_prompt()
- test_run_agent_unsetting_nesting_depth()
- test_run_agent_initializes_wip_file()
- test_run_agent_detects_complete_returns_zero()
- test_run_agent_incomplete_returns_nonzero()
- test_run_agent_cross_platform_paths()

### New: `tests/test_integration_queue_to_completion.py`

End-to-end integration tests:
- test_full_workflow_haiku_completion()
- test_full_workflow_incomplete_retry()
- test_full_workflow_multiple_agents()
- test_full_workflow_cross_platform_paths()

### New: `tests/conftest.py`

Pytest fixtures:
- temp_project (temporary directory structure)
- mock_platform_json (cross-platform testing)
- mock_subprocess (prevents real spawning)

## Acceptance Criteria

- ✅ All test files created with comprehensive scenarios
- ✅ Tests cover Windows/Linux/macOS code paths
- ✅ Error handling tested for each component
- ✅ Integration tests verify end-to-end flow
- ✅ >80% line coverage across components
- ✅ Tests are isolated with no shared state
- ✅ README documents how to run tests

## Dependencies

- Requires Q01, Q02, Q03 implementations
- Does NOT block other workorders


DEAD END - Queue worker implemented, docs superseded by current system
