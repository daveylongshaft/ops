# Work Log Rules

## Journal with echo, nothing else

Use `echo >> wip_file` to journal. One line per action, BEFORE you do it:

```bash
echo "read server.py to understand QUIT handling" >> wo/wip/TASK.md
echo "found issue at line 142 — socket not closed on timeout" >> wo/wip/TASK.md
echo "fix server.py line 142 — add s.close() in finally block" >> wo/wip/TASK.md
```

**Rules:**
- Echo BEFORE acting, not after
- Say WHAT and WHY, not just "reading X"
- No checkboxes. No Edit tool on the WIP file. No re-reading the WIP.
- Flat list of steps. Append only.
- One line per action.

## PID Stamp

First thing, stamp your PID so crash recovery knows you're alive:

```bash
AGENT_PID=$(ps -o ppid= -p $$ | tr -d ' ')
echo "PID: $AGENT_PID starting at $(date)" >> wo/wip/TASK.md
```

To check later if an agent is alive: `ps -p <PID>`. Dead PID = orphaned WIP, safe to claim.

## On Crash Recovery

Read the WIP once to find where you stopped. Then resume appending. Don't reconstruct or fake entries — if you missed journaling a step, note that it happened but wasn't logged. Fake logs are worse than no logs.

## COMPLETE

When done, append COMPLETE as the final line:

```bash
echo "COMPLETE" >> wo/wip/TASK.md
```

Then print `COMPLETE` to stdout and exit. The wrapper detects this and handles everything else.
