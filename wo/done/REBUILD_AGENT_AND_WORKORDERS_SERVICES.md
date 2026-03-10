---
urgency: P0
tags: infrastructure,critical,services,migration
requires: [python3, git]
---

# Rebuild: agent_service + workorders_service (Lost in Migration)

## Problem

The `agent` CLI command fails:
```
$ agent status
Error: Cannot find agent_service or workorders_service.
```

Root cause: These services were not migrated to the new csc_service package structure. They exist only as stubs in `/c/csc/bin/archive/services/` that point to non-existent `csc_shared.services`.

## What Needs to Happen

Recreate two service classes in `/c/csc/irc/packages/csc_service/csc_service/shared/services/`:

1. **agent_service.py** - AgentService class with methods:
   - `list()` - list available agents
   - `select(name)` - select active agent
   - `assign(workorder_path)` - assign workorder to agent
   - `status()` - show running agents and queue status
   - `stop()` - stop running agent
   - `kill()` - force kill agent
   - `tail(n)` - tail WIP journal

2. **workorders_service.py** - WorkordersService class (aka "prompts") with methods:
   - `status()` - show queue stats (ready/wip/done/hold counts)
   - `list(dirname)` - list workorders in directory
   - `read(ref)` - read workorder by number or filename
   - `add(desc, content)` - create new workorder
   - `move(ref, dirname)` - move workorder between directories
   - `edit(filename, content)` - replace workorder content
   - `append(filename, text)` - append to workorder
   - `archive(filename)` - move to archive
   - `assign(filename, agent)` - assign to agent

## Implementation Notes

- Both services should inherit from `Log` class (for logging)
- Use `Path` and `Platform()` for path resolution
- Follow one-class-per-file pattern
- Add docstrings and type hints
- Make them compatible with both old CLI calls and new service layer
- Store state using Data class (persistent JSON)

## Success Criteria

✅ `agent_service.py` exists and implements all methods
✅ `workorders_service.py` exists and implements all methods
✅ `agent status` command works without errors
✅ `agent list` returns available agents
✅ `agent select sonnet` works
✅ All workorder commands work (wo list, wo read, wo add, etc.)
✅ Integration with agent CLI completes
✅ No import errors on startup

## Urgency

**P0** - Critical infrastructure. The entire agent/workorder system depends on these services.

READY FOR IMPLEMENTATION


--- Agent Log ---
Already up to date.
Current branch main is up to date.
Invoking: gemini -y -m gemini-2.5-pro -p " " (cwd: /opt, repo: /opt/csc/tmp/gemini-2.5-pro/REBUILD_AGENT_AND_WORKORDERS_SERVICES-1773112107/repo)
[WARN] Skipping unreadable directory: /opt/csc/.config/configstore (EACCES: permission denied, scandir '/opt/csc/.config/configstore')
YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
[WARN] Skipping unreadable directory: /opt/csc/.config/configstore (EACCES: permission denied, scandir '/opt/csc/.config/configstore')
YOLO mode is enabled. All tool calls will be automatically approved.
Hook registry initialized with 0 hook entries
Error when talking to Gemini API Full report available at: /tmp/gemini-client-error-Turn.run-sendMessageStream-2026-03-10T03-08-53-102Z.json TerminalQuotaError: You have exhausted your capacity on this model. Your quota will reset after 15h36m1s.
    at classifyGoogleError (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/googleQuotaErrors.js:214:28)
    at retryWithBackoff (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/retry.js:131:37)
    at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
    at async GeminiChat.makeApiCallAndProcessStream (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:431:32)
    at async GeminiChat.streamWithRetries (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:263:40)
    at async Turn.run (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/turn.js:66:30)
    at async GeminiClient.processTurn (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/client.js:459:26)
    at async GeminiClient.sendMessageStream (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/client.js:559:20)
    at async file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/dist/src/nonInteractiveCli.js:193:34
    at async main (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/dist/src/gemini.js:492:9) {
  cause: {
    code: 429,
    message: 'You have exhausted your capacity on this model. Your quota will reset after 15h36m1s.',
    details: [ [Object], [Object] ]
  },
  retryDelayMs: 56161955.680681996
}
An unexpected critical error occurred:[object Object]

[INFO] Agent execution completed
[INFO] Log: /opt/csc/ops/logs/gemini-2.5-pro_1773112108.log


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)


--- Agent Log ---
Already up to date.
Current branch main is up to date.
Invoking: gemini -y -m gemini-2.5-pro -p " " (cwd: /opt, repo: /opt/csc/tmp/gemini-2.5-pro/REBUILD_AGENT_AND_WORKORDERS_SERVICES-1773112107/repo)
[WARN] Skipping unreadable directory: /opt/csc/.config/configstore (EACCES: permission denied, scandir '/opt/csc/.config/configstore')
YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
[WARN] Skipping unreadable directory: /opt/csc/.config/configstore (EACCES: permission denied, scandir '/opt/csc/.config/configstore')
YOLO mode is enabled. All tool calls will be automatically approved.
Hook registry initialized with 0 hook entries
Error when talking to Gemini API Full report available at: /tmp/gemini-client-error-Turn.run-sendMessageStream-2026-03-10T03-08-53-102Z.json TerminalQuotaError: You have exhausted your capacity on this model. Your quota will reset after 15h36m1s.
    at classifyGoogleError (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/googleQuotaErrors.js:214:28)
    at retryWithBackoff (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/retry.js:131:37)
    at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
    at async GeminiChat.makeApiCallAndProcessStream (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:431:32)
    at async GeminiChat.streamWithRetries (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:263:40)
    at async Turn.run (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/turn.js:66:30)
    at async GeminiClient.processTurn (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/client.js:459:26)
    at async GeminiClient.sendMessageStream (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/client.js:559:20)
    at async file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/dist/src/nonInteractiveCli.js:193:34
    at async main (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/dist/src/gemini.js:492:9) {
  cause: {
    code: 429,
    message: 'You have exhausted your capacity on this model. Your quota will reset after 15h36m1s.',
    details: [ [Object], [Object] ]
  },
  retryDelayMs: 56161955.680681996
}
An unexpected critical error occurred:[object Object]

[INFO] Agent execution completed
[INFO] Log: /opt/csc/ops/logs/gemini-2.5-pro_1773112108.log


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)
START
reading README.1shot and INDEX.txt
fixing csc_shared import in workorders_service.py
writing tests for agent_service and workorders_service
verifying no csc_shared references remain in services
COMPLETE


--- Agent Log ---
Invoking: /home/davey/.local/bin/claude --dangerously-skip-permissions --model sonnet -p - (cwd: /opt, repo: /opt/csc/tmp/sonnet/REBUILD_AGENT_AND_WORKORDERS_SERVICES-1773112399/repo)
Done. Here's what was done:

**Finding**: Both `agent_service.py` and `workorders_service.py` already existed at `/opt/csc/irc/packages/csc-service/csc_service/shared/services/` and were functional. The only actual bug was a stale import reference in `workorders_service.py:457`.

**Fix**: Changed `csc_shared.services.agent_service` → `csc_service.shared.services.agent_service` in the `assign()` method's fallback queue-worker path.

**Tests written** (not run):
- `/opt/csc/irc/tests/test_agent_service.py` — covers `list`, `select`, `status`, `stop`, `kill`, `tail`, `assign`, `_parse_front_matter`
- `/opt/csc/irc/tests/test_workorders_service.py` — covers `status`, `list`, `read`, `add`, `move`, `edit`, `append`, `archive`, `assign`, `_sanitize_filename`, `urgency`

**Verified**: `agent status`, `agent list`, `agent select sonnet`, `wo status`, `wo list ready` all work correctly.

[INFO] Agent execution completed
[INFO] Log: /opt/csc/ops/logs/sonnet_1773112400.log
