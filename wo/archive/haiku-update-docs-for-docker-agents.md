---
agent: haiku
platform: [linux, windows, android]
---

# Update Documentation for Docker Agents

## Objective

Update `CLAUDE.md` and `README.1st` with Docker agent usage, monitoring mechanics, template reference, and agent assign integration.

## Files to Modify

- `CLAUDE.md` — add Docker agent section
- `README.1st` — update Running Prompts section

## Changes to CLAUDE.md

Add a new section **after** the "Common Commands > Running the System" section (around line 60). Insert:

```markdown
### Docker Agent Execution

Run prompts using Docker-isolated agents:

```bash
# Python3 tasks (default: ollama-agent)
dc-run list                          # List ready/ prompts
dc-run #1                            # Run prompt #1
dc-run task.md                       # Run specific prompt
dc-run task.md --agent coding-agent --model python3  # Docker Python3

# Bash tasks
dc-sh list                           # Same list interface
dc-sh task.md                        # Run with coding-agent/bash
dc-sh task.md --model python3        # Override model

# Agent assign integration
agent assign task.md docker-coder    # Via agent service
```

**Monitoring** (handled by dc-agent-wrapper):
- File growth check: WIP file size polled every 30s; agent killed if no growth for 3 minutes
- STATUS: COMPLETE: agent must write this as the last line of the WIP file
- Test verification: `git diff --name-only` checked for `tests/test_*.py` changes
- Single-agent enforcement: refuses to start if another agent PID is alive in wip/

**Prompt templates** (copy and fill in for new tasks):
- `prompts/TEMPLATE_docker_python3.md` — Python3 task structure
- `prompts/TEMPLATE_docker_bash.md` — Bash task structure
```

## Changes to README.1st

Update the existing "Running Prompts (Docker)" section (around line 29-37) to include dc-sh:

```markdown
## Running Prompts (Docker)

To run a prompt from `ready/` using a Docker-based agent:
```bash
dc-run list    # Show numbered list of prompts
dc-run menu    # Interactive selection menu
dc-run #1      # Run prompt #1 (default: ollama-agent)
dc-run file.md # Run specific filename

# Bash tasks via coding-agent
dc-sh list     # Same list interface
dc-sh #1       # Run with coding-agent/bash
dc-sh file.md  # Run specific prompt as bash task
```

**Monitoring:** The wrapper monitors WIP file growth (kills stalled agents after 3 min),
checks for `STATUS: COMPLETE` at end of WIP, and verifies test files were written.

**Templates:** Copy `prompts/TEMPLATE_docker_python3.md` or `prompts/TEMPLATE_docker_bash.md`
to `prompts/ready/` as a starting point for new tasks.
```

## Important

- Do NOT rewrite the entire file — only add/replace the specific sections noted above
- Keep all existing content intact
- Match the existing markdown style (heading levels, code fence style, etc.)
- Use the Edit tool for targeted changes, not Write

## Work Log

Journal every step to this file using:
```bash
echo '<step>' >> prompts/wip/haiku-update-docs-for-docker-agents.md
```

## Success Criteria

- CLAUDE.md has Docker Agent Execution section with dc-run, dc-sh, monitoring, and templates
- README.1st Running Prompts section updated with dc-sh and monitoring info
- No existing content was removed or corrupted
- Both files parse as valid markdown

STATUS: COMPLETE
