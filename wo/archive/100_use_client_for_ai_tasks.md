# Task: Use CSC Client for AI tasks

## Context
We have updated the CSC Client (`packages/csc_client/client.py`) to support programmatic mode with:
- `--infile <file>`: Reads commands from a file.
- `--outfile <file>`: Redirects all IRC traffic and client output to a file.
- `--detach`: Runs in the background without requiring interactive TTY.

## Goal
From now on, all AI-related tasks (prompt generation, agent assignment, etc.) should be performed using the CSC Client in programmatic mode. This allows for better tracking of IRC interactions and automated task management.

## Instructions
1. When you need to issue an AI command (e.g., `AI agent assign <prompt>`), do NOT just assume it works or use a mock.
2. Create a temporary `infile` with the commands you want to run.
   Example:
   ```
   /join #general
   AI agent assign PROMPT_next_task.md
   /quit
   ```
3. Run the client:
   ```bash
   python3 packages/csc_client/client.py --infile <your_infile> --outfile <your_outfile> --detach
   ```
4. Parse the `<your_outfile>` to verify the command was received and processed correctly by the server.
5. Record the outcome in your WIP journal.

## Verification
- Confirm you can successfully assign this very task using the client (if applicable).
- Ensure all future prompts you create follow this pattern.

[ ] Implement this workflow in your own operations.
[ ] Document this change in `README.1st` or a relevant `docs/` file.

--- RESTART Wed 18 Feb 2026 10:24:44 AM GMT ---
AGENT_PID: 437647
read packages/csc_client/client.py to understand --infile --outfile --detach
create test_task_infile.txt
run the client with infile and outfile
read test_task_outfile.txt to verify commands
read README.1st to see where to add instructions
read docs/ai_clients.md to update AI client workflow
read docs/client.md to see if it fits better
update README.1st with AI task execution workflow
update docs/client.md to document programmatic usage flags
check tests/live_client_programmatic_test.py to see if it covers the new flags
fix tests/live_client_programmatic_test.py to use unique nickname
remove temp files and commit
