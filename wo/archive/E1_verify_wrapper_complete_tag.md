# Phase E1: Verify Wrapper COMPLETE Tag Detection

## Task

Verify that dc-agent-wrapper correctly detects the COMPLETE tag in WIP files and moves files accordingly.

## Requirements

The wrapper should:
1. Wait for agent to exit
2. Read the WIP file
3. Check for "COMPLETE" at the end
4. If COMPLETE found: move to prompts/done/
5. If no COMPLETE: move back to prompts/ready/
6. Always run refresh-maps
7. Always git pull/push

## Verification Steps

1. Read `bin/dc-agent-wrapper` lines 344-383 (completion detection logic)

2. Verify COMPLETE tag detection:
```python
# Should have logic like:
wip_content = prompt_file.read_text(encoding='utf-8', errors='ignore')
if "COMPLETE" in wip_content:
    agent_status = "complete"
```

3. Verify file movement:
```python
if agent_status == "complete":
    move_prompt(prompt_filename, WIP_DIR, DONE_DIR)
else:
    move_prompt(prompt_filename, WIP_DIR, READY_DIR)
```

4. Verify refresh-maps is called (line ~121):
```python
refresh_maps()
```

5. Verify git operations (lines ~128-140):
```python
run_git(["add", "-A"])
run_git(["commit", "-m", msg])
run_git(["push"])
```

## If Issues Found

Update the wrapper to ensure all these steps happen in the correct order:
1. Agent exits
2. Check COMPLETE tag
3. Move file based on tag
4. Refresh maps
5. Git commit + push

## Acceptance

- Wrapper correctly detects COMPLETE tag
- Moves to done/ when COMPLETE found
- Moves to ready/ when no COMPLETE
- Always runs refresh-maps
- Always does git operations

## Work Log
