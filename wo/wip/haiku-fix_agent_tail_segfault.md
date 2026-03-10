---
urgency: P2
description: Fix segmentation fault in agent tail command
requires: git
---

# Fix: Agent Tail Segmentation Fault

## Problem
The `agent tail` command crashes with a segmentation fault:
```
/usr/bin/bash: line 1: 460714 Segmentation fault      agent tail 30 < /dev/null
```

This happens when trying to read WIP files from queue-worker output.

## Investigation Steps
1. Identify where the segfault occurs:
   - `agent tail` command in packages/csc-client or CLI
   - Queue-worker output reading
   - File I/O operations

2. Check for:
   - Buffer overflow in file reading
   - Null pointer dereference
   - File descriptor issues
   - Memory corruption in WIP file processing

## Expected Location
- File: likely packages/csc-service/csc_service/cli/commands/agent_cmd.py
- Method: `tail` command implementation
- Issue: Reading/parsing WIP files without proper bounds checking

## Fix Approach
1. Read the agent tail implementation
2. Add bounds checking and null checks
3. Handle malformed WIP files gracefully
4. Return informative error instead of segfaulting
5. Test: Run `agent tail 30` multiple times to verify no crash

## Acceptance Criteria
- ✓ `agent tail` command no longer segfaults
- ✓ Can read WIP files safely even if corrupted
- ✓ Returns error message instead of crashing

## Note
This is non-blocking for data storage audit (which continues to complete), but should be fixed to prevent tool instability.
