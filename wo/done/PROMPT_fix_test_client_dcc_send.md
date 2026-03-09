# Task: Fix Failing Test — client_dcc_send

## What Failed

Test file: `tests/test_client_dcc_send.py`
Log file: `tests/logs/test_client_dcc_send.log`

### FAILED lines

```
tests/test_client_dcc_send.py::TestClientDccSend::test_dcc_ports_command_parsing FAILED [ 14%]
```

## Instructions

1. Read the full log at `tests/logs/test_client_dcc_send.log`
2. Identify root cause of each failure
3. Fix the **code under test**, not the test (unless the test itself is wrong)
4. `rm tests/logs/test_client_dcc_send.log` (so cron re-runs the test)
5. Commit, push, move this prompt to done. **Do NOT run pytest yourself.**


--- Agent Log ---
[run_agent] Agent: gemini-2.5-flash, Root: C:\Users\davey\AppData\Local\Temp\csc\gemini-2.5-flash\repo
[run_agent] ERROR: gemini-cli not found in PATH (run: npm install -g @google/gemini-cli)


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)
START 2026-03-04 23:40:39 PID:39348
reading test log to understand failure
checking tests directory structure
reading test_client_dcc_send.py to understand test
finding Client class implementation
reading Client class to find _handle_dcc_command
identified missing ports subcommand in _handle_dcc_command
checking git history for recent changes to ports handling
verifying ports handling implementation is complete
testing _parse_dcc_ports_spec logic
simulating argument parsing flow
final verification of complete implementation
checking for and removing test log file
verifying all test methods have implementations
verified: all methods exist, ports handling is correct, ready for test
COMPLETE
