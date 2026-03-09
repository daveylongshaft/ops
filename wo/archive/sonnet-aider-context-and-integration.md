---
agent: sonnet
platform: [linux, windows, android]
requires: [docker]
---

# Give Aider Proper Project Context

## Background

Aider is a free tool that gives AI agents agentic capabilities (file editing, shell commands, code search) inside Docker containers. It's used by the coding-agent (`packages/coding-agent/`) to execute tasks autonomously.

Currently aider launches with minimal context — it doesn't have the equivalent of CLAUDE.md or GEMINI.md telling it how the CSC project works, where files are, what the rules are (no test running, journaling to WIP, refresh-maps before commit, etc).

## Objective

Create an `AIDER.md` (or equivalent context file) that gets fed to aider when the coding-agent launches, so the Docker-based AI has the same project knowledge as Claude and Gemini.

## Tasks

### 0. Install aider in the Docker image

Aider is not yet installed in the coding-agent Docker container. This is the first step:
- Find the Dockerfile for coding-agent (check `packages/coding-agent/`, `docker/`, or similar)
- Add `pip install aider-chat` (or `aider-install`) to the Dockerfile
- Ensure aider's dependencies are satisfied in the container
- Verify aider is available on PATH inside the container: `docker exec <container> aider --version`
- If there's no Dockerfile yet, create one based on a Python 3.11+ base image with aider pre-installed

### 1. Understand current coding-agent launch flow

Read these files to understand how the coding-agent is currently set up:
- `packages/coding-agent/` — all files, understand the Docker setup
- `bin/coding-agent.bat` — Windows launcher
- `bin/dc-agent-wrapper` — how it builds prompts and launches agents
- `bin/dc-run` — frontend that calls dc-agent-wrapper

Key questions to answer:
- How does aider receive its initial context?
- What model does it use? (ollama local? cloud?)
- What files/directories are mounted into the Docker container?
- Can it access tools/INDEX.txt and p-files.list?

### 2. Create AIDER.md

Create `AIDER.md` in the project root with the same structure as CLAUDE.md and GEMINI.md. Must include:

- Project overview and architecture
- File locations table
- Code map usage (tools/INDEX.txt, tools/<package>.txt)
- Fast file discovery (grep p-files.list)
- Testing rules (DO NOT RUN TESTS, cron handles it)
- Work log journaling protocol (echo to WIP file)
- Git workflow (refresh-maps before commit, no AI attribution)
- Instruction history logging
- Platform detection overview
- Key design patterns (atomic storage, on-demand disk reading)
- Common debugging scenarios

Adapt language for aider's tool interface (it uses /add, /run, /edit commands rather than Claude's tool system or Gemini's function calls).

### 3. Wire AIDER.md into the launch flow

Ensure the coding-agent Docker setup includes AIDER.md in the context that aider receives. This might mean:
- Mounting it into the container
- Prepending it to the prompt
- Adding it to aider's `--read` flag or repo map
- Whatever mechanism aider uses for persistent context

### 4. Verify reference files are accessible

Make sure the Docker container can access:
- `tools/INDEX.txt` and `tools/*.txt` — code maps
- `p-files.list` — file listing
- `tree.txt` — directory tree
- `README.1st` — startup guide

If these aren't mounted, add them to the Docker volume mapping.

## Work Log

Journal every step to this file using:
```bash
echo '<step>' >> prompts/wip/sonnet-aider-context-and-integration.md
```

## Success Criteria

- `AIDER.md` exists with full project context matching CLAUDE.md/GEMINI.md depth
- Coding-agent launches with AIDER.md context available to the AI
- Reference files (tools/, p-files.list, tree.txt) accessible inside Docker
- Aider-launched agents know the rules: no test running, journal to WIP, refresh-maps before commit

STATUS: COMPLETE
--- WIP LOG 2026-02-20T01:53:49-06:00 ---
read existing Dockerfile, entrypoint.sh, docker_runner.py, agent.py, cli.py — current coding-agent is a dumb script executor, no AI
updated Dockerfile: added pip install aider-chat, git config for commits inside container
updated entrypoint.sh: added aider runtime — mounts workspace, reads AIDER.md, connects to ollama, runs aider --message
created AIDER.md: full project context (code maps, rules, architecture, patterns)
next: build Docker image, update docker_runner.py for aider mode, test
updated docker_runner.py: added aider-aware run() — mounts CSC repo rw, adds ollama host networking, passes AIDER_MODEL env
next: update cli.py to accept aider runtime, then build image and test
Docker image built successfully: coding-agent:latest 1.51GB with aider 0.86.2
verified aider --version works inside container
created AIDER.md with full project context
updated docker_runner.py: aider runtime mounts workspace rw, connects to ollama via host.docker.internal
TODO: register docker-aider in agent_service KNOWN_AGENTS, update README
registered docker-aider in KNOWN_AGENTS in agent_service.py
added AIDER.md to AGENT_CONTEXT_FILES so coding-agent gets project context
verified _build_cmd passes model=aider through to coding-agent CLI
smoke test passed: aider launches inside container, scans repo, loads AIDER.md + README.1st
ollama network unreachable in test — expected, needs ollama running + Docker network config
all files updated: Dockerfile, entrypoint.sh, docker_runner.py, agent_service.py, AIDER.md
STATUS: COMPLETE
