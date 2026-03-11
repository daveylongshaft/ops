---
role: pr-reviewer
priority: P0
pr: 1
---

# PR Review: #1 — audit: port missing modules from csc_old

**Repository**: daveylongshaft/irc
**Author**: daveylongshaft
**Base**: main ← audit/port-missing-modules

## PR Description

Ports modules identified as MISSING/PARTIAL in csc_old vs csc_new audit.

- Table: ops/wo/results/audit-port-table.md
- Report: ops/wo/results/audit-port-report.md

Tests written for each ported module.

## Changed Files

```
.gitignore
packages/csc-service/csc_service/bridge/__init__.py
packages/csc-service/csc_service/bridge/bridge.py
packages/csc-service/csc_service/bridge/bridge_config.example.json
packages/csc-service/csc_service/bridge/control_handler.py
packages/csc-service/csc_service/bridge/data_bridge.py
packages/csc-service/csc_service/bridge/irc.py
packages/csc-service/csc_service/bridge/irc_constants.py
packages/csc-service/csc_service/bridge/irc_normalizer.py
packages/csc-service/csc_service/bridge/irc_utils.py
packages/csc-service/csc_service/bridge/main.py
packages/csc-service/csc_service/bridge/session.py
packages/csc-service/csc_service/bridge/transports/__init__.py
packages/csc-service/csc_service/bridge/transports/base.py
packages/csc-service/csc_service/bridge/transports/tcp_inbound.py
packages/csc-service/csc_service/bridge/transports/tcp_outbound.py
packages/csc-service/csc_service/bridge/transports/udp_inbound.py
packages/csc-service/csc_service/bridge/transports/udp_outbound.py
packages/csc-service/csc_service/cli/__init__.py
packages/csc-service/csc_service/cli/commands/__init__.py
packages/csc-service/csc_service/cli/commands/config_cmd.py
packages/csc-service/csc_service/cli/commands/service_cmd.py
packages/csc-service/csc_service/cli/commands/status_cmd.py
packages/csc-service/csc_service/cli/csc_ctl.py
packages/csc-service/csc_service/clients/__init__.py
packages/csc-service/csc_service/clients/chatgpt/__init__.py
packages/csc-service/csc_service/clients/chatgpt/chatgpt.py
packages/csc-service/csc_service/clients/chatgpt/main.py
packages/csc-service/csc_service/clients/claude/__init__.py
packages/csc-service/csc_service/clients/claude/claude.py
packages/csc-service/csc_service/clients/claude/main.py
packages/csc-service/csc_service/clients/dmrbot/__init__.py
packages/csc-service/csc_service/clients/dmrbot/dmrbot.py
packages/csc-service/csc_service/clients/dmrbot/main.py
packages/csc-service/csc_service/clients/gemini/__init__.py
packages/csc-service/csc_service/clients/gemini/aliases.py
packages/csc-service/csc_service/clients/gemini/client.py
packages/csc-service/csc_service/clients/gemini/gemini.py
packages/csc-service/csc_service/clients/gemini/irc.py
packages/csc-service/csc_service/clients/gemini/macros.py
packages/csc-service/csc_service/clients/gemini/main.py
packages/csc-service/csc_service/clients/gemini/secret.py
packages/csc-service/csc_service/clients/scriptbot/csc_scriptbot/__init__.py
packages/csc-service/csc_service/clients/scriptbot/csc_scriptbot/main.py
packages/csc-service/csc_service/clients/scriptbot/csc_scriptbot/plugins/__init__.py
packages/csc-service/csc_service/clients/scriptbot/csc_scriptbot/scriptbot.py
packages/csc-service/csc_service/clients/scriptbot/pyproject.toml
packages/csc-service/csc_service/config.py
packages/csc-service/csc_service/infra/pm.py
packages/csc-service/csc_service/infra/pr_review.py
packages/csc-service/csc_service/infra/queue_worker.py
packages/csc-service/csc_service/infra/test_runner.py
packages/csc-service/csc_service/main.py
packages/csc-service/csc_service/server/__pycache__/__init__.cpython-313.pyc
packages/csc-service/csc_service/server/__pycache__/irc.cpython-313.pyc
packages/csc-service/csc_service/server/__pycache__/server.cpython-313.pyc
packages/csc-service/csc_service/server/__pycache__/server_console.cpython-313.pyc
packages/csc-service/csc_service/server/__pycache__/server_file_handler.cpython-313.pyc
packages/csc-service/csc_service/server/__pycache__/server_message_handler.cpython-313.pyc
packages/csc-service/csc_service/server/__pycache__/service.cpython-313.pyc
packages/csc-service/csc_service/server/collision_resolver.py
packages/csc-service/csc_service/server/server_s2s.py
packages/csc-service/csc_service/shared/__pycache__/__init__.cpython-313.pyc
packages/csc-service/csc_service/shared/__pycache__/channel.cpython-313.pyc
packages/csc-service/csc_service/shared/__pycache__/chat_buffer.cpython-313.pyc
packages/csc-service/csc_service/shared/__pycache__/crypto.cpython-313.pyc
packages/csc-service/csc_service/shared/__pycache__/data.cpython-313.pyc
packages/csc-service/csc_service/shared/__pycache__/irc.cpython-313.pyc
packages/csc-service/csc_service/shared/__pycache__/log.cpython-313.pyc
packages/csc-service/csc_service/shared/__pycache__/network.cpython-313.pyc
packages/csc-service/csc_service/shared/__pycache__/platform.cpython-313.pyc
packages/csc-service/csc_service/shared/__pycache__/root.cpython-313.pyc
packages/csc-service/csc_service/shared/__pycache__/secret.cpython-313.pyc
packages/csc-service/csc_service/shared/__pycache__/version.cpython-313.pyc
packages/csc-service/csc_service/shared/platform.py
packages/csc-service/csc_service/shared/services/__init__.py
packages/csc-service/csc_service/shared/services/__pycache__/__init__.cpython-313.pyc
packages/csc-service/csc_service/shared/services/__pycache__/agent_service.cpython-313.pyc
packages/csc-service/csc_service/shared/services/__pycache__/proof_service.cpython-313.pyc
packages/csc-service/csc_service/shared/services/agent_service.py
packages/csc-service/csc_service/shared/services/benchmark_service.py
packages/csc-service/csc_service/shared/services/builtin_service.py
packages/csc-service/csc_service/shared/services/run_agent_executor.py
packages/csc-service/csc_service/shared/services/stats_service/README.md
packages/csc-service/csc_service/shared/services/stats_service/__init__.py
packages/csc-service/csc_service/shared/services/stats_service/stats_service.py
packages/csc-service/csc_service/shared/services/workorders_service.py
packages/csc-service/csc_service/shared/utils/__pycache__/__init__.cpython-313.pyc
packages/csc-service/csc_service/shared/utils/__pycache__/queue_utils.cpython-313.pyc
packages/csc-service/csc_service/shared/utils/__pycache__/wip_journal.cpython-313.pyc
tests/test_bridge.py
tests/test_clients.py
tests/test_collision_resolver.py
tests/test_s2s_federation.py
tests/test_scriptbot.py
tests/test_stats_service.py
tests/test_storage.py
```

## Diff (first 60KB)

```diff
(diff unavailable)
```

---

## Your Task

Review PR #1 thoroughly using your role checklist.

For each changed file, read the full file from /opt/csc/<path> — the diff is
context only, bugs hide in what surrounds the change.

Answer:
1. Does it do what the title/description claims?
2. Is it progressive (advances the system) or regressive (undoes work, breaks invariants)?
3. Security implications? (injection, path traversal, hardcoded secrets)
4. Does it break anything outside its stated purpose?
5. Storage still atomic where needed?
6. Any import cascades break?
7. Test coverage adequate?

Post your decision:

  # Approve:
  gh pr review 1 --repo daveylongshaft/irc --approve --body "Your findings"

  # Request changes:
  gh pr review 1 --repo daveylongshaft/irc --request-changes --body "Your specific findings"

Then echo COMPLETE.


--- Agent Log ---
Already up to date.
Current branch main is up to date.
Invoking: gemini -y -m gemini-2.5-pro -p " " (cwd: /opt, repo: /opt/clones/gemini-2.5-pro/PROMPT_review_pr_daveylongshaft_irc_1_20-1773113891/repo)
[WARN] Skipping unreadable directory: /opt/csc/.config/configstore (EACCES: permission denied, scandir '/opt/csc/.config/configstore')
YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
[WARN] Skipping unreadable directory: /opt/csc/.config/configstore (EACCES: permission denied, scandir '/opt/csc/.config/configstore')
YOLO mode is enabled. All tool calls will be automatically approved.
Hook registry initialized with 0 hook entries
Error when talking to Gemini API Full report available at: /tmp/gemini-client-error-Turn.run-sendMessageStream-2026-03-10T03-38-58-115Z.json TerminalQuotaError: You have exhausted your capacity on this model. Your quota will reset after 15h5m56s.
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
    message: 'You have exhausted your capacity on this model. Your quota will reset after 15h5m56s.',
    details: [ [Object], [Object] ]
  },
  retryDelayMs: 54356955.854474
}
An unexpected critical error occurred:[object Object]

[INFO] Agent execution completed
[INFO] Log: /opt/csc/ops/logs/gemini-2.5-pro_1773113892.log


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)
