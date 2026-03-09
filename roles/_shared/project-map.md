# Project Map

Working directory: `/opt/csc`

## Finding Code

Three files exist to navigate the codebase without `ls` or `find`:

**`docs/p-files.list`** — flat list of every file. Fastest grep target:
```bash
grep "server.py" docs/p-files.list
grep "queue_worker" docs/p-files.list
```

**`docs/tree.txt`** — ASCII directory tree. Use to understand structure at a glance.

**`tools/INDEX.txt`** — every class, method, and signature. Use to find what exists and where:
```bash
grep -A3 "class Server" tools/INDEX.txt
grep "handle_privmsg" tools/INDEX.txt
```

Per-package maps in `tools/` (e.g. `tools/csc-service.txt`) give deeper API detail.

## Key Paths

| Path | What |
|------|------|
| `irc/packages/csc-service/csc_service/server/` | IRC server core |
| `irc/packages/csc-service/csc_service/shared/` | Shared library (Log, Data, Platform, Network) |
| `irc/packages/csc-service/csc_service/clients/` | AI clients (claude, gemini, chatgpt, dmrbot) |
| `irc/packages/csc-service/csc_service/bridge/` | Protocol bridge (TCP→UDP) |
| `irc/packages/csc-service/csc_service/infra/` | queue_worker, pm, test_runner, pr_review |
| `irc/packages/csc-service/csc_service/shared/services/` | Dynamic service plugins |
| `ops/agents/` | Per-agent config, queues, context |
| `ops/roles/` | Role context packages (this directory) |
| `etc/` | Configs: csc-service.json, platform.json, agent_data.json |
| `logs/` | Persistent logs |
| `docs/` | Maps, architecture docs |
| `wo/` | Workorders: ready/, wip/, done/, archive/ |
| `tests/` | Integration and unit tests |
| `bin/` | CLI tools: refresh-maps, queue-worker, test-runner |

## Inheritance Chain

```
Root → Log → Data → Version → Platform → Network → Service
```

All service classes inherit this chain. Log writes to `logs/`. Data persists to `etc/`. Platform detects system capabilities and writes to `etc/platform.json`.
