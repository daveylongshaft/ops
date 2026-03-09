# Codebase Overview

## What CSC Is

IRC-based multi-AI orchestration system. An IRC server sits at the center. AI clients (Claude, Gemini, ChatGPT, dmrbot) connect as normal IRC clients. A human CLI client connects the same way. A protocol bridge (csc-bridge) lets external IRC clients like mIRC connect via TCP.

## Component Map

```
csc-bridge (TCP:9667) ──┐
csc-claude              ├──► csc-server (UDP:9525) ──► channels.json / users.json
csc-gemini              │                              bans.json / opers.json / history.json
csc-chatgpt             │
csc-client (human) ─────┘
```

All in `irc/packages/csc-service/csc_service/`:
- `server/` — IRC server core, message handler, file handler, storage
- `shared/` — Root→Log→Data→Version→Platform→Network→Service chain
- `clients/` — claude, gemini, chatgpt, dmrbot AI clients
- `bridge/` — TCP-to-UDP protocol bridge for external IRC clients
- `infra/` — queue_worker (agent lifecycle), pm (workorder routing), test_runner, pr_review
- `shared/services/` — dynamic service plugins (agent_service, workorders_service, etc.)

## Storage: Atomic, Always

Every state change is written atomically: temp file → fsync → atomic rename. Zero data loss even on power failure mid-write. Storage files: `channels.json`, `users.json`, `opers.json`, `bans.json`, `history.json`.

Key invariant: **every state change hits disk before the handler returns.**

Oper credentials and active opers are read from disk on every access (`@property`) — editing `opers.json` takes effect immediately without restart.

## Agent Lifecycle (queue_worker)

1. PM classifies workorder, selects agent, writes to `ops/agents/<name>/queue/in/`
2. queue_worker picks up, clones repo to isolated temp dir, spawns agent
3. Agent runs in temp repo — reads `docs/p-files.list`, `tools/INDEX.txt` to navigate
4. Agent does work, journals to WIP, prints COMPLETE
5. queue_worker detects COMPLETE, commits in temp repo, pushes, pulls into main repo
6. WO moves to `wo/done/`, refresh-maps runs, main repo committed and pushed

**Agents run in temp repo clones, NEVER in `/opt/csc` directly.**

## Key Invariants

1. Storage writes are atomic — no partial writes possible
2. Oper credentials read from disk on every access
3. Channel/ban state in memory, synced to disk on every change
4. IRC names are case-insensitive, normalized internally
5. Agents run in isolated temp repo clones
6. No direct commits to main without PR review for risky changes
7. Log files are locks — delete to trigger retest, don't delete if PLATFORM_SKIP

## PR Review Policy

All code changes to server core, queue_worker, pm, or shared library require review by opus or gemini-3-pro before merging to main. See `CLAUDE.md` for full policy.
