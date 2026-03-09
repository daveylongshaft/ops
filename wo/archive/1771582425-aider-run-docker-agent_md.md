# aider-run: Docker-Based AI Agent Workflow

## Objective
Enhance `bin/aider-run` to create a complete Docker-based AI agent workflow that:
- Runs aider in Docker with CSC codebase mounted
- Manages prompts via `prompts/ready/` → `prompts/done/` system
- Automates project maintenance (refresh-maps, git push/pull)
- Maintains a journal of all work performed

## Architecture

### Docker Setup
- **Image**: `paulgauthier/aider` (official, lightweight)
- **Model**: Local ollama instance (e.g., `deepseek-coder`, `codellama`)
- **Ollama Access**: From Docker: `http://host.docker.internal:11434` (Docker Desktop)
- **Mount**: CSC codebase at `/app` in container
- **User**: Non-root user (preserve file permissions)
- **Git Config**: Must be set before docker run (not inherited)
- **Prerequisites**:
  - ollama running locally: `ollama serve`
  - Model pulled: `ollama pull deepseek-coder` (or similar coding model)

### Workflow

```
1. Verify ollama is running locally (http://localhost:11434)
2. Read prompt from prompts/ready/PROMPT_ID.md
3. Setup: git config user.* (if not set)
4. Run Docker:
   docker run -it -v $(pwd):/app paulgauthier/aider \
     --model ollama/deepseek-coder \
     --ollama-base-url http://host.docker.internal:11434 \
     --no-auto-commits \
     --message "$(cat prompt)"
5. Cleanup: refresh-maps --quick, git add, git commit, git push
6. Move: prompts/ready/PROMPT_ID.md → prompts/done/PROMPT_ID.md
7. Journal: Log timestamp, prompt ID, result to csc-logs/aider-journal.txt
```

### Key Design Decisions

**Auto-commits**: Disabled in aider (`--no-auto-commits`), manual commits after completion
**Model**: Local ollama (deepseek-coder or similar)
**Ollama Bridge**: Docker Desktop uses `host.docker.internal:11434` to reach host's ollama
**Healthcheck**: Before running aider, verify ollama is reachable via curl
**Error Handling**:
  - If ollama unreachable: exit with clear error, don't consume prompt
  - If aider fails: leave prompt in ready/, log error details
  - If maps/git fails: move prompt to done/ anyway, flag error in journal
**Journal Format**: JSON lines (one entry per line, searchable)
  - Fields: timestamp, prompt_id, status (success/error), duration_seconds, error_msg

## Files to Modify

1. **`bin/aider-run`** (complete rewrite)
   - Accept prompt file, string, or stdin
   - Validate ANTHROPIC_API_KEY
   - Launch Docker container
   - Handle prompt file routing
   - Manage git/map updates
   - Write journal entries

2. **`csc-logs/` directory** (create if needed)
   - `aider-journal.txt` - JSON log entries

## Additional Helpers (Optional)

- **`bin/aider-loop`** - Watch `prompts/ready/` and run aider-run on new files
- **`scripts/setup-git-config.sh`** - Initialize git config in repo

## Recommended Ollama Models

For 12-core 5GHz CPU with 64GB RAM, suitable coding models:

- **deepseek-coder** (6.7B or 33B) - Best code quality, fast
- **codellama** (7B, 13B, 34B) - Specialized for coding
- **neural-chat** (7B) - Fast, lightweight fallback
- **mistral** (7B, MoE variants) - Balanced speed/quality

Model selection affects quality vs speed. Start with 7B for balance, scale up to 33B if performance allows.

## Implementation Complete

### What Was Done

**1. Prerequisites Setup (Parallel Agents)**
- [x] Docker image pulled: `paulgauthier/aider` (5.45GB)
- [x] Git config set: user.name='ai-agent', user.email='ai-agent@csc.local'
- [x] Ollama verified: running in Docker, codellama:7b loaded

**2. aider-run Script (C:\csc\bin\aider-run)**
- Complete Python 3.8+ implementation
- Prerequisite checks (Docker, ollama, git config)
- Docker container orchestration with volume mounts
- Prompt file routing (ready/ > done/)
- Project maintenance (refresh-maps, git add/commit/push)
- JSON journal logging (csc-logs/aider-journal.txt)
- Windows-compatible (ASCII output, no Unicode issues)
- Model selection via --model flag (default: codellama:7b)

**3. Features**
- Read prompts from files or stdin
- Inline prompt support
- Health checks before launching aider
- Graceful error handling (leaves failed prompts in ready/)
- Maintenance failures don't block prompt completion
- Journal entries include timestamp, status, duration, errors

### Next Steps

1. Create test prompt in `prompts/ready/`
2. Run: `python3 bin/aider-run prompts/ready/TEST.md`
3. Monitor journal: `tail -f csc-logs/aider-journal.txt`
4. Optional: Create `bin/aider-loop` to watch prompts/ready/ and auto-run

### System Status
- All 4 Docker images < 20GB (12GB for ollama, 5.45GB for aider, 1.5GB for coding-agent)
- Ready for immediate use with codellama:7b or other ollama models
