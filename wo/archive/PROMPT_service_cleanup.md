# Service Cleanup: Fix Broken, Remove Redundant, Update Docs

## Task
Fix services that can't load (syntax errors, wrong class names), remove redundant services, ensure documentation matches system state.

---

## Work Log

### [X] Step 1: Check cross-service dependencies
- Verified no service imports or delegates to the ones we're changing
- ntfy uses curl — keep both
- Grepped all Python, MD, AI client system prompts — zero live references
- Only hits were in version backups and done prompts (historical)

### [X] Step 2: Sideline broken/redundant services to disabled_services/
- Moved dir_lister_service.py (broken init, redundant with builtin.list_dir)
- Moved pathinfo_service.py (syntax error, trivial)
- Moved prompts_manager.py (older broken version, extends Root not Service)

### [X] Step 3: Fix prompts_service.py
- Renamed class Prompts -> prompts (lowercase for service loader)
- Made it extend Service properly
- Changed method signatures to use *args (service loader passes individual args)
- Fixed docstring path refs: prompts.ready/ -> ready/
- Removed emoji from output (IRC-friendly)
- Removed factory function create_service()
- Added default() help method

### [NEXT] Step 4: Build agent_service.py

## Agent Service Design (revised per user spec)

### API
- `agent list` — list available AI agent backends
- `agent select <name>` — select which agent to use (persisted)
- `agent assign <prompt-filename>` — full workflow:
  1. Load README.1st + prompts/README.md into context
  2. Move prompt from ready/ to wip/
  3. Git commit, push, pull (update working copy)
  4. Read wip contents, pass everything to agent as non-interactive session
  5. Agent journals each step: echo description >> wipfile BEFORE each action
  6. On completion: write tests to tests/ dir
  7. Git commit, push, pull
  8. Move wip to done/
- `agent status` — running? PID, prompt, runtime
- `agent stop` — kill running agent
- `agent log [N]` — tail agent output log

### Available agents (detected by checking PATH)
- claude (claude CLI)
- Future: other CLI-based AI tools

### Subprocess invocation
```bash
claude --dangerously-skip-permissions -p "<assembled prompt>"
```
- Working dir: /opt/csc
- stdout/stderr → logs/agent_<timestamp>.log
- PID tracked in agent_data.json

### Assembled prompt includes (in order)
1. Contents of README.1st
2. Contents of prompts/README.md
3. Instructions: follow WIP journaling, write tests, commit/push when done
4. Contents of the WIP prompt file

### State (agent_data.json)
- selected_agent: str (default "claude")
- current_pid: int or null
- current_prompt: filename
- current_log: log path
- started_at: timestamp
- [NEXT] Writing services/agent_service.py
- [X] Writing services/agent_service.py — claude + gemini backends, tail/status/stop/assign/list/select
- [X] Verified both agent_service.py and prompts_service.py import cleanly
- [NEXT] Updating status() with easy stats and tail() to read WIP file
- [X] Updated status() with runtime, memory, log size, WIP progress stats
- [X] Updated tail() to read WIP journal instead of raw agent output
- [NEXT] Adding WIP enforcement: --append-system-prompt, CLAUDE.md priority, stale watchdog

### Session (RESTART)
- Resuming from crash at WIP enforcement step
- [X] Read current agent_service.py to understand state
- [X] Fix KNOWN_AGENTS mismatch — _detect_agents and assign both expect dict-of-dicts but KNOWN_AGENTS is dict-of-strings
- [X] Fixed _detect_agents to iterate name,binary instead of name,info["binary"]
- [X] Fixed assign() to use _build_cmd() instead of broken agent_info["build_args"]()
- [X] Added STALE_THRESHOLD_SECS (5min) and _check_stale() watchdog
- [X] Integrated stale warning into status() output
- [X] CLAUDE.md priority: handled automatically by cwd=PROJECT_ROOT, --append-system-prompt adds WIP journaling as system-level override
- [X] Both files parse cleanly (ast.parse)
- [NEXT] Review task description — check if "Update Docs" part is done
- Docs check: main docs dont reference specific services, nothing to update
- Task complete: all services fixed, agent_service built, bugs patched, watchdog added
