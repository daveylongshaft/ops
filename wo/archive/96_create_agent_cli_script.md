# Task 96: Create 'agent' CLI Shell Script

## Objective
Create a shell script `/opt/csc/bin/agent` that mirrors the functionality of the `agent_service.py` module.
This script will allow users to manage AI agents (list, select, assign, status, stop, tail) directly from the command line, without needing to go through the IRC interface or manually invoke python service commands.

## Context
The `services/agent_service.py` module manages the lifecycle of autonomous AI agents (Claude, Gemini) working on prompt tasks. It handles:
- Listing and selecting agent backends
- Assigning prompt files from `ready/` to `wip/`
- Spawning the agent process
- Monitoring status and WIP journaling
- Stopping/killing agents

We need a shell script wrapper `bin/agent` that provides a convenient CLI interface to these same operations.

## Requirements

### 1. Script Location
- Path: `/opt/csc/bin/agent`
- Executable permission: `chmod +x`

### 2. Functionality
The script should accept subcommands that map to the `agent_service` methods:

| Command | Description |
| :--- | :--- |
| `agent list` | List available AI agent backends |
| `agent select <name>` | Select which agent to use (persisted) |
| `agent assign <file>` | Assign a prompt file to the selected agent |
| `agent status` | Show status of the currently running agent |
| `agent stop` | Stop the running agent |
| `agent kill` | Kill the agent and move prompt back to ready |
| `agent tail [N]` | Tail the WIP journal log |
| `agent help` | Show usage information |

### 3. Implementation Details
- The script should likely interface with the running server (if possible) OR replicate the logic to modify the `agent_service`'s data persistence directly if offline operations are needed.
- **Preference:** If the server is running, send commands to it (via `services/csc_client` or a similar mechanism).
- **Fallback:** If the server is NOT running, or if this is intended to be a standalone tool, it might need to instantiate the `agent` service class directly or replicate the logic.
- **Decision:** Since `agent_service.py` manages *processes* (PIDs), and those processes are spawned by the service, the script should ideally communicate with the running service to ensure state consistency. However, for bootstrapping, a standalone mode might be useful.
- **Simplest Approach:** The script can be a wrapper around `packages/csc-client/main.py` that sends `AI 1 agent <command> <args>` to the server and formats the output.

### 4. Testing Strategy (CRITICAL)
- **DO NOT RUN TESTS.**
- **Rationale:** We use a cron-based test runner (`tests/run_tests.sh`) that runs automatically. Running tests manually can cause infinite failure loops if you are an AI agent trying to fix tests that you are currently running.
- **Protocol:**
    1. Write the code.
    2. Write the test file `tests/test_bin_agent.py` (checking the script exists and runs help).
    3. **STOP.** Do not execute the test.
    4. Commit your work.
    5. The cron runner will pick up the new test and report results.

## Work Log
- [ ] Read `services/agent_service.py` to understand command signatures
- [ ] Create `/opt/csc/bin/agent` script
- [ ] Implement command dispatch (likely wrapping an IRC client or using a direct service invocation if feasible)
- [ ] Make executable
- [ ] Write `tests/test_bin_agent.py`
- [ ] Commit and finish

## Success Criteria
- [ ] `bin/agent` script exists and is executable
- [ ] `agent help` prints usage
- [ ] `tests/test_bin_agent.py` exists
- [ ] NO manual test execution in the work log

