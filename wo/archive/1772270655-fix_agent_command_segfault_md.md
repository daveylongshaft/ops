# Fix Agent Command Segfault (Windows MSYS2) - CRITICAL

## Problem

Running `agent assign <wo> <agent>` on Windows MSYS2 causes a **segmentation fault**:

```
[2026-02-28 03:22:07] [agent] Queued '...' for gemini-3-flash-preview
Queued '...' for agent 'gemini-3-flash-preview'.
Segmentation fault      agent assign 4 gemini-3-flash-preview
```

## Impact

- ❌ Cannot assign workorders to agents via CLI
- ❌ Queue worker cannot function (relies on agent assign)
- ❌ Blocks the entire path-based git protection implementation
- ❌ All 7 new workorders cannot be processed without fixing this
- ⚠️ CRITICAL: System is non-functional on Windows

## Reproduction

```bash
# On Windows MSYS2:
cd /c/csc
agent assign 1 gemini-3-flash-preview
# → Segmentation fault (exit code 139)
```

## Expected Behavior

- Command runs successfully
- Workorder is assigned to agent
- No segfault / exit code 139
- Output shows: "Queued 'xxx' for agent 'gemini-3-flash-preview'."

## Investigation Required

1. **Root cause analysis:**
   - Is it in the `agent` binary/wrapper?
   - Is it in Python code (csc_shared.services.agent_service)?
   - Is it in the Workorder service?
   - Is it specific to Windows MSYS2 environment?

2. **Check these locations:**
   - `bin/agent` or `bin/agent.bat` - CLI wrapper
   - `packages/csc-shared/services/agent_service.py` - Agent service implementation
   - `packages/csc-shared/services/prompts_service.py` - Workorder service
   - Any platform-specific code that might fail on Windows

3. **Look for:**
   - Memory access violations (invalid pointer dereference)
   - Stack overflow
   - Unhandled exceptions being converted to segfaults
   - C extension modules crashing
   - Process termination that's being misreported

## Solution Approach

Once root cause is found:

1. **If it's in Python code:**
   - Add try/except to prevent segfault
   - Add platform-specific error handling
   - Test on Windows MSYS2 again

2. **If it's in the binary:**
   - Rebuild or patch the agent wrapper for Windows
   - Or provide alternate CLI method for Windows (csc-ctl?)

3. **If it's an environment issue:**
   - Document workaround for Windows users
   - Provide alternative command sequence

## Success Criteria

- [x] Segfault fixed - no exit code 139
- [x] `agent assign` command works on Windows MSYS2
- [x] Workorders are successfully assigned (appear in agents/*/queue/in/)
- [x] No regression on Linux/macOS
- [x] Queue worker can function without segfault interference

## Testing

```bash
# Test 1: Simple assignment
agent assign 1 gemini-3-flash-preview
# Expected: Exit code 0, workorder in agents/gemini-3-flash-preview/queue/in/

# Test 2: Multiple assignments
agent assign 2 opus
agent assign 3 haiku
# Expected: All succeed, no segfaults

# Test 3: Queue worker can process
queue-worker  # or start via csc-ctl
# Expected: Agent execution starts without segfault interference
```

## Priority

🔴 **CRITICAL** - Blocks all queue-based operations on Windows

## Notes

- This has been an issue for a while (user mentioned "no one wants to create the orders")
- Current workaround appears to be: assignments do work (appear in queue/in/), but segfault happens after success
- Still a blocker because it crashes the shell and prevents batch assignment
- **Once fixed, the 7 path-protection workorders can proceed normally**
