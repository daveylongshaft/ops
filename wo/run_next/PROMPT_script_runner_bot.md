---
requires: [python3]
platform: [windows, linux, macos]
---
# Script Runner Bot (No-AI IRC Service Bot)

## Goal
Create a CSC IRC client bot that has NO AI backend - it only listens for and executes service module commands. Think of it as a headless service endpoint that any other client or user can call remotely.

## What It Does
- Connects to CSC server as a normal IRC client
- Registers with nick `ScriptBot` (configurable)
- Joins configured channels
- Listens for the standard service command protocol: `scriptbot <token> <service> <method> [args]`
- Routes commands through the service.py layer (same as server uses)
- Returns results via PRIVMSG
- Also accepts `<begin file>` / `<end file>` inline module uploads
- Auto-DCC GET for receiving service modules from other clients
- No AI API calls, no LLM, no API keys needed

## Why
- Cheap always-on service endpoint (no API costs)
- Can run service modules on specific platforms (e.g., a Windows-only ScriptBot for Windows tasks)
- Acts as a remote execution agent for the project manager
- Can be deployed on any machine with Python - no API keys needed
- Multiple instances with different nicks for different purposes

## Architecture
- New package: `packages/csc-scriptbot/`
- Based on the existing client pattern (csc-claude/csc-gemini structure)
- Strips out all AI/LLM code
- Keeps: IRC connection, registration, channel join, PRIVMSG handling
- Adds: service command dispatcher, file upload handler
- Config via `settings.json`: nick, channels, server, allowed_commands

## Package Structure
```
packages/csc-scriptbot/
  main.py
  scriptbot.py          # IRC client, no AI
  settings.json         # nick, channels, server config
  services/             # local service modules (starts empty, grows via uploads)
  pyproject.toml
```

## Key Differences from AI Clients
| Feature | AI Client | ScriptBot |
|---------|-----------|-----------|
| AI API | Yes (Anthropic/Google/OpenAI) | None |
| API Key | Required | Not needed |
| Cost | Per-token | Free |
| Service modules | Yes | Yes |
| File upload | Yes | Yes |
| Channel chat | AI responses | Command responses only |
| DCC | Yes | Yes |

## Verification
1. Start server and ScriptBot
2. ScriptBot auto-joins #general
3. From human client: `PRIVMSG ScriptBot :scriptbot do builtin list_dir .`
4. ScriptBot responds with directory listing
5. Upload a custom service module via `<begin file>...<end file>`
6. Execute the uploaded module's method
