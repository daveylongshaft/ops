---
agent: sonnet
platform: [linux, windows, android]
---

# Bring Ollama Online as an IRC Client

## Background

CSC has three AI clients that connect to the IRC server as full participants:
- `packages/csc-claude/` — Claude via Anthropic API
- `packages/csc-gemini/` — Gemini via Google API
- `packages/csc-chatgpt/` — ChatGPT via OpenAI API

Each one connects to the CSC server over UDP, joins channels, receives PRIVMSG events, generates responses via their respective API, and sends replies back as PRIVMSG. They're proper IRC citizens.

Ollama currently exists only as a standalone agent (`bin/ollama-agent`) used by `dc-run` for Docker-based prompt execution. It has no IRC presence — it can't join channels, chat with users, or collaborate with other AI agents on the server.

## Objective

Create `packages/csc-ollama/` — a proper IRC client package for ollama, modeled after csc-claude/csc-gemini/csc-chatgpt. When launched, it connects to the CSC IRC server, joins channels, and responds to messages using a local ollama instance (free, no API key needed).

## Tasks

### 1. Study existing AI client architecture

Read and understand the pattern used by the existing AI clients:
- `packages/csc-claude/` — all files (main.py, client logic, API integration)
- `packages/csc-gemini/` — all files (same pattern, different API)
- `packages/csc-chatgpt/` — all files (same pattern, different API)

Document the common pattern:
- How they connect to the server (UDP, registration, JOIN)
- How they receive messages (PRIVMSG handler)
- How they call their API (request/response cycle)
- How they send responses back
- Nick registration, error handling, reconnection

### 2. Create packages/csc-ollama/

Build the package following the exact same structure as the other AI clients:

```
packages/csc-ollama/
    setup.py              # pip-installable, entry point: csc-ollama
    csc_ollama/
        __init__.py
        main.py           # Entry point, connects to IRC server
        ollama_client.py  # Ollama API integration
```

Key implementation details:
- **IRC connection**: Same UDP client pattern as csc-claude/csc-gemini
- **Nick**: `Ollama` (or configurable)
- **Ollama API**: HTTP to `localhost:11434` (or OLLAMA_HOST env var)
  - Endpoint: `POST /api/generate` or `POST /api/chat`
  - Model: configurable, default `codellama:7b` or `llama3`
- **No API key needed** — ollama is local and free
- **Channel behavior**: Join #general (or configured channels) on connect
- **Message handling**: Same as other clients — receive PRIVMSG, generate response, send PRIVMSG back
- **System prompt**: Include CSC context so ollama knows it's part of the IRC system

### 3. Create launcher scripts

- `bin/csc-ollama` — Python launcher script (same pattern as other bin/ launchers)
- `bin/csc-ollama.bat` — Windows batch wrapper

### 4. Ensure ollama is reachable

The client should check if ollama is running on startup:
- Try `GET http://localhost:11434/api/tags`
- If not available, print clear error: "Ollama not running. Start it with: ollama serve"
- Do NOT auto-start Docker compose — that's dc-agent-wrapper's job
- Just be a client that talks to an already-running ollama instance

### 5. Install and test connectivity

```bash
pip install -e packages/csc-ollama
csc-ollama  # Should connect to server, join channels
```

Verify:
- Connects to CSC server on UDP 9525
- Registers with nick "Ollama"
- Joins #general
- Responds to PRIVMSG with ollama-generated text
- Handles errors gracefully (ollama down, server down, etc.)

## Reference Files

- `tools/INDEX.txt` — code map overview
- `tools/csc-claude.txt` — Claude client API map
- `tools/csc-gemini.txt` — Gemini client API map
- `tools/csc-chatgpt.txt` — ChatGPT client API map

## Work Log

Journal every step to this file using:
```bash
echo '<step>' >> prompts/wip/sonnet-bring-ollama-online-as-irc-client.md
```

## Success Criteria

- `packages/csc-ollama/` exists with proper package structure
- `pip install -e packages/csc-ollama` installs cleanly
- `csc-ollama` connects to IRC server, joins channels, responds to messages
- Uses local ollama instance (no API key, no cloud dependency)
- Follows same architecture as csc-claude/csc-gemini/csc-chatgpt
- `bin/csc-ollama` and `bin/csc-ollama.bat` launchers exist
- Model is configurable via env var or command-line flag

STATUS: COMPLETE
