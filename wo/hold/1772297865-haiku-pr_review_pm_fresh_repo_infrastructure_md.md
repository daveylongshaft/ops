# PR Review: PM Agent Module + Fresh Repo Strategy (Commit e9f2fbee)

**Reviewer**: Opus (architecture & security focus)
**Scope**: Critical infrastructure changes affecting workorder orchestration and repository management

## Code Changes to Review

```
Modified Files:
- packages/csc-service/csc_service/infra/pm.py (enhanced)
- packages/csc-service/csc_service/infra/queue_worker.py (fresh repo strategy)
- packages/csc-service/csc_service/main.py (use run_cycle_safe)
- tests/test_pm_module.py (fixed imports)
- tests/test_queue_worker.py (fixed imports + fresh repo tests)

Commit: e9f2fbee
Author: ai-agent
Date: 2026-02-28
```

## PR Review Checklist

### Architecture & Design
- [ ] Fresh repo per workorder strategy sound? (unique suffix generation, cleanup on success)
- [ ] PM cascade selection logic robust? (6-tier fallback chain, API key awareness)
- [ ] Self-healing mechanism safe? (opus self-fix scope limits, no infinite loops)
- [ ] Batching logic correct? (same-kind grouping, anthropic-only, respects priority)
- [ ] State persistence atomic? (pm_state.json, agent_metrics, api_keys sections)
- [ ] Integration points clean? (pm ↔ queue-worker ↔ agent-service)

### Security & Safety
- [ ] Fresh repo cleanup safe? (move_repo_to_trash uses shutil.move, handles errors)
- [ ] No path traversal issues? (all paths use pathlib.Path, no string concatenation)
- [ ] API key handling secure? (exhaustion detection, rotation, no leaks)
- [ ] Permission/access control? (who can trigger opus self-fix, what can it modify)
- [ ] Resource limits enforced? (AGENT_MAX_TOTAL_RUNTIME_SECONDS = 3600s, git timeouts)
- [ ] Error messages safe? (no secrets leaked in logs)

### Cross-Platform Compatibility
- [ ] Windows MSYS2 compatible? (path handling, subprocess, signal handling)
- [ ] Linux compatible? (os.kill, signal.SIGTERM, path separators)
- [ ] macOS compatible? (subprocess calls, file operations)
- [ ] subprocess.run calls use proper shell flags? (shell=True only where needed)
- [ ] Signal handling cross-platform? (is_pid_alive uses ctypes on Windows)
- [ ] Temp paths cross-platform? (uses platform.json csc_agent_work or fallback)

### Edge Cases & Error Handling
- [ ] What if .git/rebase-merge exists? (code clears it, good)
- [ ] What if git clone fails? (exception raised, agent not spawned, work blocked)
- [ ] What if move_repo_to_trash fails? (tries direct shutil.rmtree, logs error)
- [ ] What if git push fails? (repo NOT moved to trash, kept for retry)
- [ ] What if agent repo doesn't exist when checking completion? (handled gracefully)
- [ ] What if pm_state.json is corrupted? (_load_state returns default, continues)
- [ ] What if multiple agents try to process same workorder? (queue/work/ lock prevents it)
- [ ] Stale PID handling? (is_pid_alive checks correctly, cleans work dir if dead)

### Performance & Resource Management
- [ ] Repo cloning every cycle expensive? (yes, but isolation benefit worth it)
- [ ] Trash directory grows unbounded? (should have cleanup policy, not mentioned)
- [ ] pm_state.json grows unbounded? (cleanup_stale_state handles this)
- [ ] Agent metrics memory usage? (per-agent tracking OK, bounded by agent count)
- [ ] Journal log file size? (appends forever, should rotate/trim)
- [ ] Git operations timeouts reasonable? (120s clone, 60s pull/push, 30s add/commit)

### Testing & Validation
- [ ] test_pm_module.py tests critical paths? (cascade, batching, classification, priority)
- [ ] test_queue_worker.py covers fresh repo? (unique suffix, trash move, push failure handling)
- [ ] Mocking appropriate? (patch _load_state, subprocess.run, etc.)
- [ ] What if tests fail? (test-runner generates PROMPT_fix_test_*.md, cycle repeats)

### Integration Issues
- [ ] Fresh repo timestamp collisions possible? (timestamp + random hex should be unique)
- [ ] Queue-worker ↔ PM state sync? (mark_completed/mark_failed called at right time)
- [ ] API key rotation side effects? (re-queues prompt with new key, correct)
- [ ] Orphan recovery interacts with fresh repos? (orphan recovery moves WIP back to ready, correct)
- [ ] Haiku debug workorder format correct? (matches expected prompt format)
- [ ] Opus self-fix can't break other code? (scope limited to pm.py, can't modify queue-worker)

### Code Quality
- [ ] Consistent naming? (pm.py uses snake_case, matches codebase)
- [ ] Docstrings complete? (functions documented, behavior clear)
- [ ] Type hints? (no type hints, matches codebase style)
- [ ] Comments helpful? (explain WHY, not WHAT, mostly good)
- [ ] No dead code? (all functions used or exported)
- [ ] No circular imports? (pm ← csc_service, queue_worker ← pm, clean)

## Critical Questions for Reviewer

1. **Fresh repo disk usage**: Is it OK to create a new repo per workorder? Cleanup via .trash/ adequate?
2. **Stale state handling**: Is ORPHAN_TIMEOUT_SECS = 120s reasonable? Too aggressive?
3. **API key rotation**: Should we rate-limit how fast we rotate? Prevent thrashing?
4. **PM self-healing scope**: Should opus be able to modify queue_worker or agent_service too?
5. **Journal log rotation**: Should old journal entries be trimmed or rotated?

## Expected Outcome

- [ ] No critical security issues
- [ ] No breaking changes to existing interfaces
- [ ] Cross-platform compatibility confirmed
- [ ] Edge cases handled appropriately
- [ ] Performance impact acceptable
- [ ] Ready for test-runner validation cycle

---

**If approved**: Mark COMPLETE and tests will validate functionality
**If issues found**: Document them, create fix workorders, block production startup


--- Agent Log ---
[run_agent] Agent: gemini-3-pro, Root: C:\Users\davey\AppData\Local\Temp\csc\gemini-3-pro\repo
[run_agent] Starting Gemini (gemini-2.5-pro) for gemini-3-pro
YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
YOLO mode is enabled. All tool calls will be automatically approved.
C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11
var consoleProcessList = getConsoleProcessList(shellPid);
                         ^

Error: AttachConsole failed
    at Object.<anonymous> (C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11:26)
    at Module._compile (node:internal/modules/cjs/loader:1761:14)
    at Object..js (node:internal/modules/cjs/loader:1893:10)
    at Module.load (node:internal/modules/cjs/loader:1481:32)
    at Module._load (node:internal/modules/cjs/loader:1300:12)
    at TracingChannel.traceSync (node:diagnostics_channel:328:14)
    at wrapModuleLoad (node:internal/modules/cjs/loader:245:24)
    at Module.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:154:5)
    at node:internal/main/run_main_module:33:47

Node.js v24.13.0
C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11
var consoleProcessList = getConsoleProcessList(shellPid);
                         ^

Error: AttachConsole failed
    at Object.<anonymous> (C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11:26)
    at Module._compile (node:internal/modules/cjs/loader:1761:14)
    at Object..js (node:internal/modules/cjs/loader:1893:10)
    at Module.load (node:internal/modules/cjs/loader:1481:32)
    at Module._load (node:internal/modules/cjs/loader:1300:12)
    at TracingChannel.traceSync (node:diagnostics_channel:328:14)
    at wrapModuleLoad (node:internal/modules/cjs/loader:245:24)
    at Module.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:154:5)
    at node:internal/main/run_main_module:33:47

Node.js v24.13.0
C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11
var consoleProcessList = getConsoleProcessList(shellPid);
                         ^

Error: AttachConsole failed
    at Object.<anonymous> (C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11:26)
    at Module._compile (node:internal/modules/cjs/loader:1761:14)
    at Object..js (node:internal/modules/cjs/loader:1893:10)
    at Module.load (node:internal/modules/cjs/loader:1481:32)
    at Module._load (node:internal/modules/cjs/loader:1300:12)
    at TracingChannel.traceSync (node:diagnostics_channel:328:14)
    at wrapModuleLoad (node:internal/modules/cjs/loader:245:24)
    at Module.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:154:5)
    at node:internal/main/run_main_module:33:47

Node.js v24.13.0
C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11
var consoleProcessList = getConsoleProcessList(shellPid);
                         ^

Error: AttachConsole failed
    at Object.<anonymous> (C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11:26)
    at Module._compile (node:internal/modules/cjs/loader:1761:14)
    at Object..js (node:internal/modules/cjs/loader:1893:10)
    at Module.load (node:internal/modules/cjs/loader:1481:32)
    at Module._load (node:internal/modules/cjs/loader:1300:12)
    at TracingChannel.traceSync (node:diagnostics_channel:328:14)
    at wrapModuleLoad (node:internal/modules/cjs/loader:245:24)
    at Module.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:154:5)
    at node:internal/main/run_main_module:33:47

Node.js v24.13.0
C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11
var consoleProcessList = getConsoleProcessList(shellPid);
                         ^

Error: AttachConsole failed
    at Object.<anonymous> (C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11:26)
    at Module._compile (node:internal/modules/cjs/loader:1761:14)
    at Object..js (node:internal/modules/cjs/loader:1893:10)
    at Module.load (node:internal/modules/cjs/loader:1481:32)
    at Module._load (node:internal/modules/cjs/loader:1300:12)
    at TracingChannel.traceSync (node:diagnostics_channel:328:14)
    at wrapModuleLoad (node:internal/modules/cjs/loader:245:24)
    at Module.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:154:5)
    at node:internal/main/run_main_module:33:47

Node.js v24.13.0
C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11
var consoleProcessList = getConsoleProcessList(shellPid);
                         ^

Error: AttachConsole failed
    at Object.<anonymous> (C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11:26)
    at Module._compile (node:internal/modules/cjs/loader:1761:14)
    at Object..js (node:internal/modules/cjs/loader:1893:10)
    at Module.load (node:internal/modules/cjs/loader:1481:32)
    at Module._load (node:internal/modules/cjs/loader:1300:12)
    at TracingChannel.traceSync (node:diagnostics_channel:328:14)
    at wrapModuleLoad (node:internal/modules/cjs/loader:245:24)
    at Module.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:154:5)
    at node:internal/main/run_main_module:33:47

Node.js v24.13.0
^CTerminate batch job (Y/N)? 


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)


--- Agent Log ---
[run_agent] Agent: gemini-3-pro, Root: C:\Users\davey\AppData\Local\Temp\csc\gemini-3-pro\repo
[run_agent] Starting Gemini (gemini-2.5-pro) for gemini-3-pro
YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
YOLO mode is enabled. All tool calls will be automatically approved.
C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11
var consoleProcessList = getConsoleProcessList(shellPid);
                         ^

Error: AttachConsole failed
    at Object.<anonymous> (C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11:26)
    at Module._compile (node:internal/modules/cjs/loader:1761:14)
    at Object..js (node:internal/modules/cjs/loader:1893:10)
    at Module.load (node:internal/modules/cjs/loader:1481:32)
    at Module._load (node:internal/modules/cjs/loader:1300:12)
    at TracingChannel.traceSync (node:diagnostics_channel:328:14)
    at wrapModuleLoad (node:internal/modules/cjs/loader:245:24)
    at Module.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:154:5)
    at node:internal/main/run_main_module:33:47

Node.js v24.13.0
C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11
var consoleProcessList = getConsoleProcessList(shellPid);
                         ^

Error: AttachConsole failed
    at Object.<anonymous> (C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11:26)
    at Module._compile (node:internal/modules/cjs/loader:1761:14)
    at Object..js (node:internal/modules/cjs/loader:1893:10)
    at Module.load (node:internal/modules/cjs/loader:1481:32)
    at Module._load (node:internal/modules/cjs/loader:1300:12)
    at TracingChannel.traceSync (node:diagnostics_channel:328:14)
    at wrapModuleLoad (node:internal/modules/cjs/loader:245:24)
    at Module.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:154:5)
    at node:internal/main/run_main_module:33:47

Node.js v24.13.0
C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11
var consoleProcessList = getConsoleProcessList(shellPid);
                         ^

Error: AttachConsole failed
    at Object.<anonymous> (C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11:26)
    at Module._compile (node:internal/modules/cjs/loader:1761:14)
    at Object..js (node:internal/modules/cjs/loader:1893:10)
    at Module.load (node:internal/modules/cjs/loader:1481:32)
    at Module._load (node:internal/modules/cjs/loader:1300:12)
    at TracingChannel.traceSync (node:diagnostics_channel:328:14)
    at wrapModuleLoad (node:internal/modules/cjs/loader:245:24)
    at Module.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:154:5)
    at node:internal/main/run_main_module:33:47

Node.js v24.13.0
C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11
var consoleProcessList = getConsoleProcessList(shellPid);
                         ^

Error: AttachConsole failed
    at Object.<anonymous> (C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11:26)
    at Module._compile (node:internal/modules/cjs/loader:1761:14)
    at Object..js (node:internal/modules/cjs/loader:1893:10)
    at Module.load (node:internal/modules/cjs/loader:1481:32)
    at Module._load (node:internal/modules/cjs/loader:1300:12)
    at TracingChannel.traceSync (node:diagnostics_channel:328:14)
    at wrapModuleLoad (node:internal/modules/cjs/loader:245:24)
    at Module.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:154:5)
    at node:internal/main/run_main_module:33:47

Node.js v24.13.0
C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11
var consoleProcessList = getConsoleProcessList(shellPid);
                         ^

Error: AttachConsole failed
    at Object.<anonymous> (C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11:26)
    at Module._compile (node:internal/modules/cjs/loader:1761:14)
    at Object..js (node:internal/modules/cjs/loader:1893:10)
    at Module.load (node:internal/modules/cjs/loader:1481:32)
    at Module._load (node:internal/modules/cjs/loader:1300:12)
    at TracingChannel.traceSync (node:diagnostics_channel:328:14)
    at wrapModuleLoad (node:internal/modules/cjs/loader:245:24)
    at Module.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:154:5)
    at node:internal/main/run_main_module:33:47

Node.js v24.13.0
C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11
var consoleProcessList = getConsoleProcessList(shellPid);
                         ^

Error: AttachConsole failed
    at Object.<anonymous> (C:\Users\davey\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@lydell\node-pty\conpty_console_list_agent.js:11:26)
    at Module._compile (node:internal/modules/cjs/loader:1761:14)
    at Object..js (node:internal/modules/cjs/loader:1893:10)
    at Module.load (node:internal/modules/cjs/loader:1481:32)
    at Module._load (node:internal/modules/cjs/loader:1300:12)
    at TracingChannel.traceSync (node:diagnostics_channel:328:14)
    at wrapModuleLoad (node:internal/modules/cjs/loader:245:24)
    at Module.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:154:5)
    at node:internal/main/run_main_module:33:47

Node.js v24.13.0
^CTerminate batch job (Y/N)? 


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)
