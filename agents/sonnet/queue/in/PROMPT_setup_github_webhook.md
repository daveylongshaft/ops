---
role: system-architect
priority: P0
tags: [linux, webhook, apache, github-app]
---

# TASK: Deploy GitHub Webhook Listener for csc-csc-agent

**Context**: 
We have successfully configured the GitHub App `csc-csc-agent` (ID: 3060746) for PR reviews. To eliminate polling delays, we need to transition to a webhook-based architecture using the Apache server on `facingaddictionwithhope.com`.

## 1. Environment Verification
First, verify if this machine is the target host:
- Check if `facingaddictionwithhope.com` resolves to a local IP address on this machine.
- If **NOT** the host: Log "SKIP: Not the webhook host" and move to the next workorder.
- If **IS** the host: Proceed with the following steps.

## 2. Webhook Listener Implementation
Create a lightweight Python listener (using Flask or FastAPI) at `packages/csc-service/csc_service/infra/webhook_listener.py`:
- It must listen on `127.0.0.1:5000` (or a configurable port).
- It must implement GitHub Webhook Signature Verification using a `GITHUB_WEBHOOK_SECRET` from `.env`.
- **Payload Handling**:
    - Listen for `pull_request` events.
    - When a PR is opened or synchronized:
        1. Extract repo, PR number, and branch info.
        2. Immediately trigger `bin/pr-review-agent.sh` (which now uses the App token).
- Ensure the listener is added to `csc-service` as a background daemon or managed process.

## 3. Apache Configuration
Configure Apache to act as a reverse proxy:
- Target URL: `https://facingaddictionwithhope.com/csc-webhook`
- Proxy to: `http://127.0.0.1:5000/webhook`
- Ensure `mod_proxy` and `mod_proxy_http` are enabled.
- Add the configuration to the appropriate site-available file.

## 4. GitHub App Update
Once the listener is live:
1. Provide the user with a randomly generated `GITHUB_WEBHOOK_SECRET`.
2. Instruct the user to update the GitHub App settings:
   - Webhook: **Active**
   - Payload URL: `https://facingaddictionwithhope.com/csc-webhook`
   - Secret: (The generated secret)
   - Events: **Pull request**

## Validation
- Send a test delivery from the GitHub App settings.
- Verify the listener receives it, validates the signature, and triggers the review cycle.

Echo COMPLETE when the listener is deployed and the proxy is configured.


--- Agent Log ---
Already up to date.
Current branch main is up to date.
Invoking: gemini -y -m gemini-2.5-pro -p " " (cwd: /opt, repo: /opt/clones/gemini-2.5-pro/PROMPT_setup_github_webhook-1773228444/repo)
[WARN] Skipping unreadable directory: /opt/csc/.config/configstore (EACCES: permission denied, scandir '/opt/csc/.config/configstore')
YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
[WARN] Skipping unreadable directory: /opt/csc/.config/configstore (EACCES: permission denied, scandir '/opt/csc/.config/configstore')
YOLO mode is enabled. All tool calls will be automatically approved.
Hook registry initialized with 0 hook entries
Error when talking to Gemini API Full report available at: /tmp/gemini-client-error-Turn.run-sendMessageStream-2026-03-11T11-27-54-988Z.json TerminalQuotaError: You have exhausted your capacity on this model. Your quota will reset after 11h38m47s.
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
    message: 'You have exhausted your capacity on this model. Your quota will reset after 11h38m47s.',
    details: [ [Object], [Object] ]
  },
  retryDelayMs: 41927071.271611
}
An unexpected critical error occurred:[object Object]

[INFO] Agent execution completed
[INFO] Log: /opt/csc/ops/logs/gemini-2.5-pro_1773228445.log


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)


--- Agent Log ---
Already up to date.
Current branch main is up to date.
Invoking: gemini -y -m gemini-2.5-pro -p " " (cwd: /opt, repo: /opt/clones/gemini-2.5-pro/PROMPT_setup_github_webhook-1773228444/repo)
[WARN] Skipping unreadable directory: /opt/csc/.config/configstore (EACCES: permission denied, scandir '/opt/csc/.config/configstore')
YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
[WARN] Skipping unreadable directory: /opt/csc/.config/configstore (EACCES: permission denied, scandir '/opt/csc/.config/configstore')
YOLO mode is enabled. All tool calls will be automatically approved.
Hook registry initialized with 0 hook entries
Error when talking to Gemini API Full report available at: /tmp/gemini-client-error-Turn.run-sendMessageStream-2026-03-11T11-27-54-988Z.json TerminalQuotaError: You have exhausted your capacity on this model. Your quota will reset after 11h38m47s.
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
    message: 'You have exhausted your capacity on this model. Your quota will reset after 11h38m47s.',
    details: [ [Object], [Object] ]
  },
  retryDelayMs: 41927071.271611
}
An unexpected critical error occurred:[object Object]

[INFO] Agent execution completed
[INFO] Log: /opt/csc/ops/logs/gemini-2.5-pro_1773228445.log


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)
