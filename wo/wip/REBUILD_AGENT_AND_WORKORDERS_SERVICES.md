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
