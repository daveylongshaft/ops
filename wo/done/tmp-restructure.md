---
urgency: P2
tags: infrastructure, agent-pipeline
---

# Restructure Agent Temp Directory Layout

## Goal

Fix agent temp directory structure so:
- spawn_cwd = CSC_ROOT (agents run from project root)
- All paths are relative from project root
- Even limited agents (gemini) can see ops/, tmp/, and code repo from one tree

## Current State (already done)

- platform.py line 709: `csc_agent_work = str(temp_root)` -- CORRECT (no /csc suffix)
- platform.json: `csc_agent_work: C:\csc\tmp` -- CORRECT
- Clones land at: `C:\csc\tmp\clones\<agent>\<wo>-<ts>\repo`

## What Still Needs Changing

### 1. orders.md-template (ops/agents/templates/orders.md-template)

Current line 1: `You are an AI coding agent running from /opt/.`
Change to: `You are an AI coding agent. Your working directory is the CSC project root.`

Current line 5: `**Code repo**: <agent_repo_rel_path>/ -- your isolated clone of irc.git`
Change to: `**Code repo**: tmp/clones/<agent_name>/<wo_stem>/repo/ -- your isolated clone`

Remove all `<agent_repo_rel_path>` placeholders. Replace with the actual relative path
injected at spawn time (see queue_worker change below).

Update ALL per-agent templates too (9 files in ops/agents/*/orders.md-template).

### 2. agent_service.py - _run_generate_orders_md_script()

Current (line 601): `repo_path = str(self.PROJECT_ROOT).replace("\\", "/")`
This line computes a replacement for `<agent_repo_rel_path>` but never actually uses it
(the replace call was already removed in a prior fix).

Remove the dead `repo_path` line. The template should use literal `tmp/clones/...` paths
or a new `<clone_rel_path>` placeholder that queue_worker fills at spawn time.

### 3. queue_worker.py - process_inbox() and agent executor

The `AGENT_EXECUTOR` import (`from csc_service.shared.agent_executor import AgentExecutor`)
points to the OLD stub at `packages/csc-service/csc_service/shared/agent_executor.py`.
This stub:
- Has no cwd set on Popen (inherits parent process cwd)
- Has hardcoded model names ('claude-2', 'gemini-pro')
- Never reads orders.md

Need to either:
a) Replace with `RunAgentExecutor` from `irc/packages/.../run_agent_executor.py` which
   already sets `cwd=str(self.project_root)`, OR
b) Fix the old stub to set `cwd=str(CSC_ROOT)` and use proper model selection

Recommended: option (a) -- switch to RunAgentExecutor.

### 4. Before spawning: inject clone path into orders.md

In queue_worker.py, after `create_agent_temp_repo()` returns the clone path:
- Read orders.md from the agent's queue dir
- Compute relative path from CSC_ROOT to clone: `tmp/clones/<agent>/<wo>-<ts>/repo`
- Replace `<clone_rel_path>` placeholder with the actual relative path
- Write back orders.md

This ensures the agent knows exactly where its code repo is, using a path
relative to its cwd (which is CSC_ROOT).

### 5. Clean up stale clones in tmp/

There are leftover clones from failed runs:
```
tmp/csc/clones/gemini-2.5-pro/tmp-restructure-*/
tmp/csc/clones/opus/upgrade_server-*/
tmp/csc/clones/sonnet/tmp-restructure-*/
```
These are under `tmp/csc/` (the OLD path). Can be safely deleted.
The new path is `tmp/clones/` (no extra /csc/).

Wait -- `create_agent_temp_repo()` at line 224 still uses:
```python
clones_base = (_plat.agent_work_base or CSC_ROOT / "tmp" / "csc") / "clones"
```
Since `agent_work_base` is now `C:\csc\tmp`, this resolves to `C:\csc\tmp\clones` -- CORRECT.
But the fallback still says `"tmp" / "csc"` -- fix fallback to just `"tmp"`.

## Files to Change

1. `ops/agents/templates/orders.md-template` - rewrite environment section
2. `ops/agents/*/orders.md-template` (9 per-agent copies) - same changes
3. `irc/packages/csc-service/csc_service/shared/services/agent_service.py` - remove dead repo_path line
4. `irc/packages/csc-service/csc_service/infra/queue_worker.py`:
   - Switch AGENT_EXECUTOR to RunAgentExecutor
   - Add clone path injection into orders.md before spawn
   - Fix fallback in `create_agent_temp_repo()` line 224
5. Clean up `tmp/csc/` directory (old path remnants)

## Verification

After changes:
- `agent select haiku && agent assign <test-wo>` should work
- Agent log should show cwd = CSC_ROOT
- orders.md in queue should have real relative clone path, not placeholder
- Agent should be able to read ops/wo/wip/<file> via relative path from cwd
