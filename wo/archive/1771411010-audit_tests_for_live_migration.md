# Task: Audit Tests for Live Server Migration

## Goal
Investigate the `tests/` directory and identify all mock-based unit tests that should be converted to live integration tests using the CSC client in programmatic mode.

## Instructions

1.  **Analyze existing tests:**
    *   List all test files in `tests/`.
    *   Identify which tests are mock-based (e.g., using `unittest.mock`, `MagicMock`) and which are already live integration tests (e.g., using `subprocess` to run the client).
    *   Verify if mock-based tests provide coverage for server services or core features that should be tested against a live server.

2.  **Create Migration Prompts:**
    *   For each mock-based test identified, create a NEW prompt in `prompts/ready/`.
    *   Naming convention: `MIGRATE_TEST_<test_name>.md`.
    *   The prompt must instruct the agent to:
        *   Rewrite the test to use the CSC client in **programmatic mode**.
        *   **Persistent Client:** Use a persistent client process (e.g., using a FIFO for input or keeping the process running) for up to one hour to avoid repeated setup/teardown.
        *   **Execution:** Send actual IRC commands (e.g., `AI agent assign ...`, `/join`, etc.) to the live server.
        *   **Verification:** Verify results by parsing the client's outfile.
        *   **Cleanup:** Remove the old test log file (e.g., `rm tests/logs/test_feature.log`) to force a re-run by the cron job.
        *   **Automation:** DO NOT run the tests manually; the cron job will execute them.
        *   **Git Workflow:** Add, commit, push, and pull changes after rewriting.

3.  **Agent Assignment Workflow:**
    *   Instruct that these prompts should be executed one at a time using `AI agent assign`.
    *   Verify completion and perform git commit/push/pull between each assignment.

4.  **Journaling:**
    *   Keep the WIP journal updated with findings and the list of generated prompts.

5.  **Finalization:**
    *   Once all migration prompts are created, move this audit prompt to `done/`.

AGENT_PID: 441152
--- RESTART Wed Feb 18 10:45:00 UTC 2026 ---
Listing test files to begin audit
Created 17 migration prompts in prompts/ready/
