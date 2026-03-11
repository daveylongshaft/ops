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
