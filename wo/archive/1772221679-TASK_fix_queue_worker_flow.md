# Task: Fix Queue-Worker Complete Flow

**Status**: IN PROGRESS

## Complete Flow Requirements

```
PM: agent select → agent assign (ready→wip, generate orders.md→queue/in)
↓
Queue-worker Cycle:
  1. Check queue/work/ is EMPTY (no active agent)
  2. If empty, pick first orders.md from queue/in/
  3. Move orders.md: queue/in/ → queue/work/
  4. git add . && git commit -m "assigning task <wo> to <agent>" && git push
  5. Verify push succeeded
  6. git pull in agent's temp repo (created by Claude Code CLI)
  7. Run agents/<name>/bin/run_agent.py (or agents/template/ fallback)
  8. Agent works non-interactively, logs output
↓
Queue-worker Next Cycle:
  1. Check agent PID still running
  2. If finished:
     - git add . && git commit -a && git push (commit agent's changes)
     - git pull in main repo (download updated WIP)
     - Check for COMPLETE marker in workorders/wip/<name>.md
     - Move orders.md: queue/work/ → queue/out/
     - Clean up queue/out/ after X minutes
```

## Current Issues

1. ❌ Queue-worker doesn't check if queue/work/ is EMPTY before picking new task
2. ❌ Queue-worker is copying WIP file into queue/work/ (WRONG - only orders.md goes there)
3. ❌ Queue-worker git push verification not implemented
4. ❌ Queue-worker doesn't pull agent's temp repo before spawn_agent
5. ❌ Queue-worker doesn't pull updated WIP from GitHub after agent finishes
6. ❌ Confusion between orders.md (system procedures) and workorders (actual tasks)

## Work Log

### Step 1: Fix process_inbox() - DONE ✅
- ✅ Removed WIP copying logic (only orders.md in queue/work/)
- ✅ Added queue/work/ emptiness check before processing queue/in/
- ✅ Implemented git push verification
- ✅ Cleaned up dead code (unreachable legacy handling)
- Commit: ab0da5f0

Key changes:
- Check if any agent has active work in queue/work/ before processing inbox
- Extract workorder filename from orders.md before moving it
- Verify workorder exists in workorders/wip/
- git add agents/, git commit, git push with proper error handling
- Only spawn agent if all setup succeeds

### Step 2: Verify run_agent.py - DONE ✅
- ✅ run_agent.py already does git pull at startup (line 305)
- ✅ Extracts WIP filename from orders.md
- ✅ Provides setup instructions with absolute paths
- ✅ Instructs agent to commit/push changes
- No changes needed

### Step 3: Verify process_work() - DONE ✅
- ✅ Already does git pull when agent finishes (line 604-608)
- ✅ Checks for COMPLETE marker in WIP
- ✅ Moves workorder to done/ or back to ready/ as appropriate
- ✅ Moves orders.md from queue/work/ to queue/out/
- ✅ Commits and pushes final state
- No changes needed

### Step 4: Test full cycle - READY
Flow is now correct:
1. PM: agent select → agent assign (moves ready→wip, generates orders.md→queue/in)
2. Queue-worker: Checks queue/work/ empty → moves orders.md (in→work)
3. Queue-worker: git add . && git commit && git push (orders.md now in GitHub)
4. Queue-worker: spawns agent (agent's temp repo from Claude Code will git pull to get it)
5. run_agent.py: git pull (gets orders.md and WIP file into agent's temp repo)
6. Agent: works non-interactively, commits/pushes changes back to GitHub
7. Queue-worker (next cycle): agent PID finished → git pull (gets updated WIP)
8. Queue-worker: checks COMPLETE marker → moves wip→done/ (or back to ready/)
9. Queue-worker: moves orders.md (work→out) → git commit/push



VERIFIED COMPLETE - Opus PM audit 2026-02-27: implementation confirmed in codebase
