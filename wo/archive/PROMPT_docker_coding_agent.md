# Task: Design and Implement Self-Hosted Coding Agent in Docker

## Goal
Create a self-hosted coding agent service that runs in Docker. The agent should:
1. Accept coding tasks/prompts from a queue
2. Execute code (Python, Bash, Node.js, etc.) in isolated Docker containers
3. Return results to the CSC agent service framework
4. Be registered as a new agent backend in the agent_service.py agent list

## Context: CSC Project
This CSC (Client-Server-Commander) project is an IRC-based multi-AI orchestration system.

**Key Architecture:**
- Server runs on UDP port 9525 with IRC protocol
- Multiple AI clients connect as normal IRC clients (Claude, Gemini, ChatGPT)
- Agent service manages task queues and spawns agent processes
- Each agent backend is a CLI binary (e.g., `claude`, `gemini`)
- New agents can be added by registering in agent_service.py's KNOWN_AGENTS dict

**Current agents:**
- `haiku`, `sonnet`, `opus` - Claude models
- `gemini-2.5-flash`, `gemini-3-flash`, `gemini-3-pro` - Gemini models

**Your goal:** Add Docker-based code execution agents to this list.

## Requirements

### 1. Docker Container Design
- Lightweight base image (Alpine or minimal Python)
- Accept a script/code as stdin or via env var
- Execute in isolation with timeout (configurable, default 30s)
- Return stdout/stderr and exit code
- Support installing deps (pip, npm, apt) if script requests
- Optional: network access control

### 2. Agent CLI Binary
- Create `coding-agent` command that agent_service.py can call
- Usage: `coding-agent -m MODEL -p "SCRIPT_TEXT" [OPTIONS]`
- Match interface of claude/gemini CLIs:
  - `-m MODEL`: Runtime (python3, bash, node18, python3.11, etc)
  - `-p PROMPT`: Script content to execute
  - `--timeout SECS`: Override default timeout
  - `-y`: Auto-yes (non-interactive)
  - `--image IMAGE`: Docker image to use
- Output format: plain stdout/stderr (agent service parses it)

### 3. Docker Image
Build custom image with:
- Python 3.10+ (base)
- Node.js 18+
- Bash/sh
- Common tools: curl, git, jq, wget
- Minimal size (use multi-stage build if needed)
- Publish locally or to Docker Hub

### 4. Integration with CSC Agent Service
Update `packages/csc_shared/services/agent_service.py`:

**Add to KNOWN_AGENTS dict:**
```python
"docker-python": {
    "binary": "coding-agent",
    "model": "python3",
    "label": "Docker-Based Python (Isolated)"
},
"docker-bash": {
    "binary": "coding-agent",
    "model": "bash",
    "label": "Docker-Based Bash (Isolated)"
},
"docker-node": {
    "binary": "coding-agent",
    "model": "node18",
    "label": "Docker-Based Node.js (Isolated)"
},
```

**Update `_build_cmd()` to recognize `coding-agent` binary and format commands correctly.**

### 5. Package Structure
```
packages/coding-agent/
├── coding_agent/
│   ├── __init__.py
│   ├── agent.py           # Main logic (Docker interaction)
│   ├── docker_runner.py   # Wrapper for docker run commands
│   └── cli.py             # Click CLI entry point
├── docker/
│   ├── Dockerfile         # Container definition
│   └── docker-compose.yml # For local dev (optional)
├── bin/
│   └── coding-agent       # Shell wrapper calling cli.py
├── setup.py               # pip install entry
├── README.md              # Usage docs
└── tests/
    ├── test_agent.py      # Unit tests
    └── test_integration.py # Integration tests
```

### 6. Security Constraints
- Run containers with `--cap-drop=ALL --cap-add=NET_BIND_SERVICE` (or drop NET entirely)
- Read-only filesystem: `--read-only --tmpfs /tmp`
- No privileged mode
- Memory limit: `--memory 512m`
- CPU limit: `--cpus 1.0`
- Timeout enforcement with SIGKILL fallback
- No host filesystem mounts except /tmp (tmpdir only)
- User: run as non-root (uid 1000)

### 7. Error Handling
- **Timeout:** Kill container, return "TIMEOUT: Script exceeded N seconds"
- **Exec error:** Return stderr + exit code
- **Docker unavailable:** Check `docker ps`, return graceful error
- **Image pull failure:** Retry once, then error
- **OOM/Resource limits:** Return resource exhaustion error

## Deliverables
1. **packages/coding-agent/** - Complete Python package
2. **CLI binary `coding-agent`** - Installed to /usr/local/bin or ~/.local/bin
3. **Dockerfile** - Builds reproducible image
4. **Integration:** Update agent_service.py, test with `AI do agent select docker-python`
5. **README.md** - Usage examples, Docker setup, troubleshooting
6. **Tests** - Unit tests for agent, integration test if possible

## Success Criteria

## Implementation Notes

**1. Docker Execution Pattern:**
```python
docker run --rm --memory 512m --cpus 1.0 --timeout 30s \
  --cap-drop=ALL \
  --read-only --tmpfs /tmp \
  -e SCRIPT="$(cat script.py)" \
  my-coding-agent:latest python3
```

**2. CLI Pattern (matching claude/gemini):**
```bash
coding-agent -y -m python3 -p "print(42)" --timeout 10
# Output: 42
```

**3. Agent Service Integration:**
When user does `AI do agent select docker-python`:
- agent_service.py calls: `coding-agent -y -m python3 -p "[FULL_PROMPT_CONTENT]"`
- Output goes to log file
- User can view with `AI do agent tail`

**4. Dependency Installation:**
If prompt says "pip install requests", container should auto-detect and install on first run (cache layer).

## References
- **agent_service.py:** `packages/csc_shared/services/agent_service.py` (shows _build_cmd pattern)
- **Docker docs:** https://docs.docker.com/ (security best practices)
- **Claude CLI:** Used as interface model (check `claude --help`)

---

**Start by:**
1. Read agent_service.py to understand agent interface
2. Design Docker image with minimal footprint
3. Implement Python CLI with Click
4. Test locally: `coding-agent -m python3 -p "print(123)"`
5. Register in agent_service.py
6. Test via IRC: `AI do agent assign PROMPT_test.md`

work starting on docker coding agent - reading agent_service.py to understand interface
creating package structure

created docker_runner.py - Docker execution wrapper
created agent.py - CodingAgent logic
created cli.py - Click CLI interface
created __init__.py - Package initialization
created Dockerfile - Multi-stage minimal image
created entrypoint.sh - Container entry script
created setup.py - Package installation
created README.md - Comprehensive documentation
created test_agent.py - Unit tests
created test_integration.py - Integration tests (Docker-based)
created bin/coding-agent - Shell wrapper
created docker-compose.yml - Development compose
created tests/test_coding_agent.py - CSC framework integration tests
updated agent_service.py - registered docker-python, docker-bash, docker-node agents

commit created - 8d6bd1e
push complete
moving to done
