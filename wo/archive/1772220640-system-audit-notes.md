# System Audit Notes - Prompt Executor Pipeline

## Current System Architecture

**3 background services** managed by `csc-service --daemon` (or individually via `csc-ctl`):

1. **PM** (`packages/csc-service/csc_service/infra/pm.py`) - Scans `ready/`, classifies workorders by filename pattern, picks cheapest capable agent, calls `agent.bat select` + `agent.bat assign`, generates `orders.md` in `queue/in/`. Tracks attempts in `pm_state.json`, escalates on failure (gemini-2.5-flash -> gemini-3-pro -> opus -> human-review). Max 3 attempts before escalation.

2. **Queue Worker** (`packages/csc-service/csc_service/infra/queue_worker.py`) - Moves `orders.md` from `queue/in/` to `queue/work/`, git commit+push, git pull in temp repo, spawns run_agent script, monitors PID, on finish: commit+push temp repo, pull main, check COMPLETE, route to done/ or ready/. One task at a time.

3. **Test Runner** (`packages/csc-service/csc_service/infra/test_runner.py`) - Scans `tests/test_*.py` for missing logs, runs them via pytest, generates `PROMPT_fix_<test>.md` for failures and `PROMPT_run_<test>.md` for platform-gated tests.

**Orchestration:** `csc-service/main.py` runs all 3 in a loop: git_sync.pull() -> test_runner.run_cycle() -> queue_worker.run_cycle() -> pm.run_cycle() -> git_sync.push_if_changed(). Poll interval from csc-service.json (default 60s).

**Agent scripts:** Each agent has `agents/<name>/bin/run_agent.{sh,bat,py}`. Template in `agents/templates/`. Cloud agents (claude/gemini) use run_agent.py which auto-detects and calls claude CLI or npx gemini-cli. Local agents (codellama/deepseek/qwen/dmr_qwen_task_runner) use cagent exec with their cagent.yaml.

**Git flow for tasks:**
- PM assigns -> moves WO from ready/ to wip/, generates orders.md in queue/in/
- Queue worker moves orders.md to queue/work/, git add+commit+push main repo
- Queue worker git pull in agent temp repo (at C:\Users\davey\AppData\Local\Temp\csc\<agent>\repo\)
- Queue worker spawns run_agent with cwd=temp repo
- Agent works in temp repo, journals to workorders/wip/<filename>
- On finish: queue worker commit+push from temp repo, pull to main repo
- Check COMPLETE marker -> done/ or ready/, move orders.md to queue/out/

## Known Issues (Current Broken State)

### Critical
1. **Temp repo git rebase conflicts** - haiku's temp repo stuck in detached HEAD from failed rebase. queue_worker.py now has reset+clean logic but it's aggressive. Need reliable temp repo recovery.
2. **PID file naming** - Currently uses `<workorder>.pid`, user wants fixed name `agent.pid` - one agent at a time, always same filename.
3. **PM calls agent.bat via subprocess** - brittle, shell-dependent. Should call agent_service module directly (Python-to-Python).
4. **Double orders.md generation** - PM generates orders.md AND agent_service._run_generate_orders_md_script() also generates it. Duplicated logic.
5. **Double git handling** - queue_worker does its own git pull/push, AND csc-service main loop does git_sync.pull()/push_if_changed(). Potential conflicts when both run.

### Functional
6. **refresh-maps not found** - queue_worker looks in SCRIPT_DIR for refresh-maps but it's in bin/. Path resolution broken.
7. **Stale workorder looping** - build_stats_tracking_system has 7 attempts, keeps bouncing ready->wip->ready. No backoff or cooldown.
8. **bin/ scripts missing** - No queue-worker.bat or test-runner.bat in bin/ (they exist only as infra modules)
9. **run_agent.sh template hardcodes claude** - Only handles claude CLI, not gemini or local. The .py version handles all but .sh only does claude.
10. **PM agent roster incomplete** - Only has gemini-2.5-flash, gemini-3-pro, haiku, opus. Missing sonnet, chatgpt, all local agents.

### Design
11. **Workorder stays in main repo wip/ while agent works in temp repo** - agent tail can't see live progress unless it checks temp repo (now fixed in agent_service.py)
12. **No cooldown between retries** - PM immediately re-assigns failed workorders on next cycle
13. **No credit exhaustion handling in PM** - queue_worker has it but PM doesn't know about it
14. **agent_data.json tracks only one task** - stale after task finishes, not cleaned up reliably
15. **Queue worker and PM both try to handle the same workorder lifecycle** - unclear ownership boundaries

## File Locations

| File | Purpose |
|------|---------|
| `packages/csc-service/csc_service/infra/queue_worker.py` | Queue worker (standalone + embedded) |
| `packages/csc-service/csc_service/infra/pm.py` | Project Manager |
| `packages/csc-service/csc_service/infra/test_runner.py` | Test runner |
| `packages/csc-service/csc_service/infra/git_sync.py` | Git pull/push for main loop |
| `packages/csc-service/csc_service/main.py` | csc-service daemon main loop |
| `packages/csc-service/csc_service/cli/csc_ctl.py` | csc-ctl CLI |
| `packages/csc-service/csc_service/shared/services/agent_service.py` | Agent service (list/select/assign/status/tail) |
| `packages/csc-service/csc_service/shared/services/queue_worker_service.py` | QueueWorkerService class (IRC interface) |
| `agents/templates/orders.md-template` | Orders template with `<wip_file_relative_pathspec>` placeholder |
| `agents/templates/generate_orders_md.bat` | Script to fill template |
| `agents/templates/run_agent.py` | Universal agent runner (claude/gemini/local) |
| `agents/templates/run_agent.sh` | Bash agent runner (claude only) |
| `agents/templates/run_agent.bat` | Windows agent runner (calls run_agent.py) |
| `pm_state.json` | PM assignment tracking |
| `agent_data.json` | Current agent tracking (pid, prompt, log) |
| `csc-service.json` | Service config (enable/disable, poll interval, clients) |
| `platform.json` | Platform detection (paths, capabilities) |

## Desired Flow (User's Description)

1. `wo list ready` to find a workorder, or `wo add` to make one
2. `agent select <model>` to choose agent
3. `agent assign wo.md` - moves WO from ready to wip, creates orders.md in queue/in
4. Queue worker (running in background) picks up orders.md:
   - Moves orders.md from queue/in to queue/work
   - Git commit+push main repo (so files are in GitHub)
   - Git pull in agent's temp repo (so files are in temp repo)
   - cd to agent temp repo, run the run_agent script from agents/<name>/bin/ (or template fallback)
   - run_agent script needs NO command line args - it finds orders.md and WIP from its known paths
5. When script ends, next queue-worker cycle:
   - Detects dead PID
   - Commits changes using AI log as commit message
   - Updates maps (refresh-maps)
   - Routes WO to done/ if COMPLETE, back to ready/ if not
   - Moves orders.md to queue/out/ (renamed with unixtime)
   - Git push
6. Only 1 workorder at a time
7. Same workorder retried until complete before moving to next
8. PID file: always named `agent.pid`, not `<workorder>.pid`
9. Test runner runs separately, generates fix workorders for failures
10. All hangs, git issues, API credit deficits resolved automatically by script

## User Requirements for PID File

- Name: `agent.pid` (fixed, not per-workorder)
- One agent at a time across all dirs
- Same name every time in every dir you run an agent in
