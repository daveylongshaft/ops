# Task: Migrate test_module_manager_service.py to Live Client Integration Test

## Goal
Rewrite the mock-based unit test `tests/test_module_manager_service.py` to be a live integration test using the CSC client in programmatic mode, communicating with a live server.

## Instructions

1.  **Preparation:**
    *   Identify the core functionality tested in `tests/test_module_manager_service.py`.
    *   Determine the IRC commands (e.g., `AI ...`, `/join`, `/msg`) needed to replicate these tests on a live server.
    *   Create a temporary input file for the CSC client.

2.  **Rewrite the Test:**
    *   Create a new test file: `tests/live_module_manager_service_test.py`.
    *   **Persistent Client:** The test script must start a CSC client process in background mode (e.g., using `--detach` and a FIFO/named pipe for input) and keep it online for up to one hour or until the test suite completes. This avoids the overhead of repeated registration.
    *   **Programmatic Mode:** Send commands to the client via its input mechanism.
    *   **Verification:** Parse the client's outfile (specified with `--outfile`) to verify that the server's responses match expected outcomes.
    *   **Automation:** The script should be runnable by the project's test runner/cron. It should NOT require manual intervention.

3.  **Cleanup & Integration:**
    *   Remove the old mock-based test log if it exists: `rm tests/logs/test_module_manager_service.log`.
    *   The old test file `tests/test_module_manager_service.py` should remain (or be marked as deprecated) but its log removal forces the system to recognize the need for a fresh run (via the new live test).
    *   Ensure the new test is discovered by the test runner (e.g., `pytest` or `unittest` discovery).

4.  **Git Workflow:**
    *   `git add tests/live_module_manager_service_test.py`
    *   `git commit -m "Migrate test_module_manager_service.py to live client integration test"`
    *   `git pull && git push`

5.  **Important Notes:**
    *   DO NOT run the test manually during this task. Let the system cron handle it.
    *   Ensure the client nickname used in the test is unique to avoid collisions.
    *   The client should stay up for the duration of the tests (up to 1 hour).

AGENT_PID: 440697
