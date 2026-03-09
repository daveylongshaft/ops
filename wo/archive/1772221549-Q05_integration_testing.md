---
requires: ["python3", "git", "pytest"]
platform: ["windows", "linux", "macos"]
agent: opus
depends_on: ["Q02", "Q03", "Q04"]
---

# Q05: Integration Testing - Complete End-to-End Queue System

## Goal

Create comprehensive integration tests verifying the complete workflow.

## Tasks

1. **Create Test Suite Structure**
   - Location: tests/test_queue_system/
   - Files: test_agent_service_queue.py, test_run_agent_executor.py, test_queue_worker_service.py, test_integration_flow.py, conftest.py

2. **Test agent_service.assign() Queue Integration**
   - Test assign() creates queue directory structure
   - Test assign() moves file from ready/ to queue/in/
   - Test assign() creates WIP and metadata
   - Test error cases

3. **Test RunAgentExecutor Class**
   - Test load queue entry and metadata
   - Test prepare environment
   - Test build command
   - Test journaling
   - Test error handling

4. **Test QueueWorkerService Methods**
   - Test cycle() scans and processes
   - Test success and failure cases
   - Test metadata tracking

5. **Create Full Integration Test**
   - Complete workflow: assign → queue → execute → complete

6. **Test Cross-Platform Paths**
   - Test with platform.json fixtures
   - Verify correct notation for each platform

7. **Test Error Recovery**
   - Test crash recovery and retry logic

## Files to Create

- tests/test_queue_system/__init__.py
- tests/test_queue_system/conftest.py
- tests/test_queue_system/test_agent_service_queue.py
- tests/test_queue_system/test_run_agent_executor.py
- tests/test_queue_system/test_queue_worker_service.py
- tests/test_queue_system/test_integration_flow.py

## Acceptance Criteria

- [x] Test suite covers all major code paths
- [x] Tests for error cases
- [x] Cross-platform paths tested
- [x] Integration test covers full flow
- [x] All tests have docstrings

## Dependencies

- Depends on: Q02, Q03, Q04
- Enables: Q06


## Work Log
START 2026-02-26 - Opus designing pure Python queue system


DEAD END - Queue worker implemented, docs superseded by current system
