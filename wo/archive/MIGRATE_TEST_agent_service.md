# Task: Migrate test_agent_service.py to Live Client Integration Test

## Goal
Rewrite the mock-based unit test `tests/test_agent_service.py` to be a live integration test using the CSC client in programmatic mode, communicating with a live server.

## Instructions

1.  **Preparation:**
    *   Identify the core functionality tested in `tests/test_agent_service.py`.
    *   Determine the IRC commands (e.g., `AI ...`, `/join`, `/msg`) needed to replicate these tests on a live server.
    *   Create a temporary input file for the CSC client.

2.  **Rewrite the Test:**
    *   Create a new test file: `tests/live_agent_service_test.py`.
    *   **Persistent Client:** The test script must start a CSC client process in background mode (e.g., using `--detach` and a FIFO/named pipe for input) and keep it online for up to one hour or until the test suite completes. This avoids the overhead of repeated registration.
    *   **Programmatic Mode:** Send commands to the client via its input mechanism.
    *   **Verification:** Parse the client's outfile (specified with `--outfile`) to verify that the server's responses match expected outcomes.
    *   **Automation:** The script should be runnable by the project's test runner/cron. It should NOT require manual intervention.

3.  **Cleanup & Integration:**
    *   Remove the old mock-based test log if it exists: `rm tests/logs/test_agent_service.log`.
    *   The old test file `tests/test_agent_service.py` should remain (or be marked as deprecated) but its log removal forces the system to recognize the need for a fresh run (via the new live test).
    *   Ensure the new test is discovered by the test runner (e.g., `pytest` or `unittest` discovery).

4.  **Git Workflow:**
    *   `git add tests/live_agent_service_test.py`
    *   `git commit -m "Migrate test_agent_service.py to live client integration test"`
    *   `git pull && git push`

5.  **Important Notes:**
    *   DO NOT run the test manually during this task. Let the system cron handle it.
    *   Ensure the client nickname used in the test is unique to avoid collisions.
    *   The client should stay up for the duration of the tests (up to 1 hour).

AGENT_PID: 440697

read tests/test_agent_service.py to understand current coverage
read tests/live_client_programmatic_test.py for implementation patterns
read services/agent_service.py to identify IRC commands
read packages/csc_client/client.py to check infile handling
modify services/agent_service.py to add test-agent
create tests/live_agent_service_test.py
cleanup old test logs
check for reload capability in module_manager_service.py
read packages/csc_server/server_message_handler.py to check command routing
update tests/live_agent_service_test.py with correct AI commands
git add and commit
check git status to ensure all files staged
check symlink status of services directory
check services/agent_service.py symlink
git add the actual file path for agent_service.py
read tests/run_tests.sh to check discovery rules
push changes
verify log removal
check for new test log
check results of new test
check for fix prompt
move prompt to done
