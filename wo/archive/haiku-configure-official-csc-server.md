---
requires: [python3, git]
platform: [windows, linux]
agent: haiku
---

# Configure Official CSC Server: facingaddictionwithhope.com

## Objective

Ensure all CSC clients, servers, and CLI tools use `facingaddictionwithhope.com:9525` as the official CSC server.

## Current Status

- `.env` has `CSC_SERVER_HOSTNAME=facingaddictionwithhope.com` ✓
- `csc-client` reads from .env ✓
- Other clients (claude, gemini, chatgpt) may use hardcoded defaults ✗

## Required Changes

### 1. Update All AI Clients

**Files to modify:**
- `packages/csc-claude/claude.py`
- `packages/csc-gemini/gemini.py`
- `packages/csc-chatgpt/chatgpt.py`
- `packages/csc-docker/docker_client.py`

**Pattern:**
```python
# Old (hardcoded)
super().__init__("config.json", host="127.0.0.1", port=9525)

# New (read from .env)
import os
host = os.getenv("CSC_SERVER_HOSTNAME", "127.0.0.1")
port = int(os.getenv("CSC_SERVER_PORT", "9525"))
super().__init__("config.json", host=host, port=port)
```

### 2. Update Server Configuration

**File: `packages/csc-server/main.py`**
- Read `CSC_SERVER_HOSTNAME` from .env
- Use it in server bind/listen setup if needed
- Document that server runs on the configured hostname

### 3. Update CLI Tools

**Files to verify:**
- `bin/sm-run` — Uses localhost (OK, local execution)
- `bin/dc-run` — Uses localhost (OK, Docker-based)
- `bin/agents` — Check if it uses server hostname
- `bin/prompts` — Check if it uses server hostname

### 4. Update README Files

**Files to update:**
- `README.md` — Add section: "Official Server: facingaddictionwithhope.com"
- `CLAUDE.md` — Update server connection instructions
- Each client README (csc-claude, csc-gemini, etc.)
- `.env` documentation

### 5. Update CLAUDE.md Instructions

Replace any references to `localhost` or `127.0.0.1` with `facingaddictionwithhope.com`.

**Search for:**
- "127.0.0.1"
- "localhost"
- "9525" (without hostname context)

**Replace with:**
- "facingaddictionwithhope.com"
- With context about .env configuration

## Testing

For each client, verify:
1. Client starts without error
2. Client connects to `facingaddictionwithhope.com:9525`
3. Check logs for "Connected to facingaddictionwithhope.com"

```bash
# Test each client
csc-claude 2>&1 | grep -i "facingaddictionwithhope\|connected"
csc-gemini 2>&1 | grep -i "facingaddictionwithhope\|connected"
csc-chatgpt 2>&1 | grep -i "facingaddictionwithhope\|connected"
csc-docker 2>&1 | grep -i "facingaddictionwithhope\|connected"
```

## Deliverables

- [ ] All AI clients read CSC_SERVER_HOSTNAME from .env
- [ ] All AI clients connect to facingaddictionwithhope.com by default
- [ ] CLI tools documented (sm-run/dc-run are local, so OK)
- [ ] README files updated with official server info
- [ ] CLAUDE.md updated with hostname references
- [ ] Tests verify all clients connect to correct server
- [ ] Commit with message: "Configure all clients to use official server: facingaddictionwithhope.com"

## Commits Expected

```
[config] Update all clients to read CSC_SERVER_HOSTNAME from .env
[docs] Update README files with official server information
[docs] Update CLAUDE.md with facingaddictionwithhope.com references
```
--- RESTART Thu, Feb 19, 2026  1:41:35 PM ---
AGENT_PID: 1004
