# Agent Task Templates

Templates in this directory are used by the agent-wrapper to create standardized task files in agent queue directories.

## Variables

Templates support these placeholders:
- `{prompt_name}` - Human-readable task name
- `{agent_name}` - Agent identifier (e.g., "ollama-qwen")
- `{timestamp}` - ISO 8601 timestamp
- `{prompt_filename}` - Actual WIP filename
- `{prompt_content}` - Full prompt text
- `{model}` - Model being used
- `{pid}` - Process ID (filled after spawn)

## Usage

When `agent assign <prompt> <agent>` is called, the wrapper:
1. Reads `default.md`
2. Substitutes variables
3. Copies to `agents/<agent>/queue/in/<prompt>.md`
4. Queue worker picks up and processes
