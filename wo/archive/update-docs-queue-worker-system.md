# Update Documentation: Queue Worker System

## Task

Update project documentation to reflect the new queue-worker lifecycle system.

The old system used `agent-wrapper` to synchronously spawn agents and handle git operations.
The new system uses `queue-worker` as a full lifecycle manager:

### New Architecture

1. `agent assign <prompt>` creates a ticket in `agents/<agent>/queue/in/`
2. `queue-worker` (runs every ~2 min via cron/Task Scheduler) picks it up:
   - `git pull`
   - Moves prompt from `ready/` -> `wip/`
   - Moves queue file from `in/` -> `work/`
   - Assembles prompt: README.1shot + agents/<name>/context/* + WIP
   - Spawns AI agent in background
   - Notes PID in queue file
   - Exits (non-blocking)
3. Next queue-worker run:
   - Checks PID - if still running, monitors WIP growth (stale detection)
   - If agent finished: checks WIP for COMPLETE
     - COMPLETE -> prompt moves to `done/`, queue `work/` -> `out/`
     - No COMPLETE -> prompt moves back to `ready/`
   - Runs `refresh-maps`, `git commit` (with WIP summary in message), `git push`

### Files to Update

1. **README.1st** - Update "Running Prompts" and "AI Task Execution" sections
2. **prompts/README.md** - Update workflow to mention queue-worker instead of wrapper
3. **README.1shot** - Update "What Happens When You Exit" to mention queue-worker instead of wrapper
4. **SCHEDULER_SETUP.md** - Verify queue-worker setup instructions are current

### What NOT to Change

- Don't change the actual code
- Don't create new files
- Just update the docs to match the new reality

## Work Log

DEAD END
