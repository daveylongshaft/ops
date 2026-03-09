---
requires: [python3, docker, git]
platform: [docker]
---
# Verify Prompts Archive Command Integration

## Recommended Agent: docker-coder

## Goal
Verify the correct implementation and functionality of the `prompts archive` command, including its presence and routing in shell scripts and service modules, and its end-to-end functionality via IRC commands using `csc-client` against a `csc-server`.

## Work Log
AGENT_PID: [AGENT_PID_HERE] starting at [TIMESTAMP_HERE]

## Steps for the Docker Agent:

1.  **Preparation: Ensure Docker Environment**
    *   Confirm Docker is running and `coding-agent:latest` image is available.
    *   The agent should operate within a cloned repository mounted into the Docker container.

2.  **Verification of Code Changes (Static Analysis):**
    *   **Check `bin/prompts`**: Read `bin/prompts` to verify:
        *   The `archive` command is listed in the main `Usage` section.
        *   The `archive` command is listed in the `COMMANDS` section within `print_help()`.
        *   The `elif command == 'archive':` block exists in `main()` and routes to `service.archive()`.
    *   **Check `packages/csc-shared/services/prompts_service.py`**: Read `packages/csc-shared/services/prompts_service.py` to verify:
        *   The `archive` method exists.
        *   The `ALL_DIRS` list in `csc_shared.utils.queue_utils.QueueDirectories` (which is implicitly imported) includes "archive".
        *   The `default` method's usage message includes the `archive` command.
    *   **Check `packages/csc-shared/utils/queue_utils.py`**: Read `packages/csc-shared/utils/queue_utils.py` to verify:
        *   `ARCHIVE = "archive"` constant exists.
        *   `ALL_DIRS` includes `ARCHIVE`.
        *   `self.dirs` mapping includes `self.ARCHIVE: self.base / "archive"`.

3.  **Functional Testing (IRC Integration):**
    *   **Setup a Local `csc-server`**: Run a `csc-server` instance within the Docker environment. This can be done by installing `csc-server` in editable mode and running `csc-server`.
    *   **Prepare `csc-client` for Programmatic Use**: The `csc-client` should be used in programmatic mode (`python packages/csc-client/client.py --infile <infile> --outfile <outfile>`).
    *   **Test Case 1: Successful Archiving**
        *   Create an `infile.txt` for `csc-client` to add a prompt: `AI <token> prompts add "Test Archive" : Test content for archive.`
        *   Run `csc-client` with `infile.txt`. Verify the prompt is created in `ready/`.
        *   Create another `infile.txt` to move the prompt to `done/`: `AI <token> prompts move <filename> done`
        *   Run `csc-client`. Verify the prompt is in `done/`.
        *   Create another `infile.txt` to edit the prompt in `done/` to add "verified complete" as the last line. (This requires reading the file, appending the line, and then using `AI <token> prompts edit <filename> : <new_content>`).
        *   Run `csc-client`. Verify the prompt is edited.
        *   Create another `infile.txt` to archive the prompt: `AI <token> prompts archive <filename>`
        *   Run `csc-client`.
        *   **Verification**: Check that the prompt file is now in `prompts/archive/`. Use `prompts list archive` via `csc-client`.
    *   **Test Case 2: Archiving Failure (Invalid Last Line)**
        *   Repeat steps to create a prompt and move it to `done/`.
        *   Edit the prompt with an *invalid* last line (e.g., "invalid content").
        *   Attempt to archive: `AI <token> prompts archive <filename>`
        *   **Verification**: Ensure the command returns an error message indicating invalid last line, and the file remains in `prompts/done/`.
    *   **Test Case 3: Archiving Failure (Not in done/)**
        *   Create a prompt in `ready/`.
        *   Attempt to archive it: `AI <token> prompts archive <filename>`
        *   **Verification**: Ensure the command returns an error message indicating the file is not in `done/`, and the file remains in `prompts/ready/`.

4.  **Final Cleanup and Reporting:**
    *   **Commit Changes**: If any test setup files or temporary prompt files were left, commit their deletion.
    *   **Report**: Summarize the verification results.
    *   **Move Prompt**: Move this `docker-coder-verify_prompts_archive_command.md` prompt to `prompts/done/`.
