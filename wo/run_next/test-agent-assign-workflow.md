---
requires: [python3, git]
platform: [windows, linux]
---

# Test: Agent Assign Workflow - Verify Queue File Creation

## Task

Test the new simplified agent_service.py assign() method to verify:
1. Workorder moves from ready/ to wip/
2. Agent-specific template is read
3. <wip_file_relative_pathspec> is regex replaced
4. Combined file is written to agents/<agent>/queue/in/
5. Journal every step to WIP file per the template requirement

## Verification Steps

1. Check that queue/in/ file contains:
   - Original template content with WIP path substituted
   - Original workorder content appended
2. Verify WIP file exists and contains journal entries
3. Confirm file paths are correct

## Expected Outcome

- workorders/ready/test-agent-assign-workflow.md moved to workorders/wip/
- agents/<agent>/queue/in/test-agent-assign-workflow.md created with combined content
- All work journaled to WIP file
- System ready for queue-worker to pick up and execute


PID: 27840 agent: gemini-3-pro starting at 2026-02-25 19:40:45

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)
