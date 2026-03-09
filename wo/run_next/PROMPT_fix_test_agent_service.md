# Task: Fix Failing Test — agent_service

## What Failed

Test file: `tests/test_agent_service.py`
Log file: `tests/logs/test_agent_service.log`

### FAILED lines

```
tests/test_agent_service.py::TestAgentService::test_assign_flow FAILED   [ 12%]
tests/test_agent_service.py::TestAgentService::test_assign_queues_workorder FAILED [ 25%]
tests/test_agent_service.py::TestAgentService::test_list FAILED          [ 37%]
tests/test_agent_service.py::TestAgentService::test_select FAILED        [ 50%]
tests/test_agent_service.py::TestAgentService::test_status_running FAILED [ 62%]
tests/test_agent_service.py::TestAgentService::test_status_stale FAILED  [ 75%]
tests/test_agent_service.py::TestAgentService::test_tail FAILED          [100%]
FAILED tests/test_agent_service.py::TestAgentService::test_assign_flow - Asse...
FAILED tests/test_agent_service.py::TestAgentService::test_assign_queues_workorder
FAILED tests/test_agent_service.py::TestAgentService::test_list - AssertionEr...
FAILED tests/test_agent_service.py::TestAgentService::test_select - Assertion...
FAILED tests/test_agent_service.py::TestAgentService::test_status_running - F...
FAILED tests/test_agent_service.py::TestAgentService::test_status_stale - Fil...
FAILED tests/test_agent_service.py::TestAgentService::test_tail - FileNotFoun...
```

## Instructions

1. Read the full log at `tests/logs/test_agent_service.log`
2. Identify root cause of each failure
3. Fix the **code under test**, not the test (unless the test itself is wrong)
4. `rm tests/logs/test_agent_service.log` (so cron re-runs the test)
5. Commit, push, move this prompt to done. **Do NOT run pytest yourself.**


--- Agent Log ---
[run_agent] Agent: gemini-2.5-flash, Root: C:\Users\davey\AppData\Local\Temp\csc\gemini-2.5-flash\repo
[run_agent] ERROR: gemini-cli not found in PATH (run: npm install -g @google/gemini-cli)


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)
