# Create Agent Template System

## Objective

Create the template system for standardized agent task files.

## Context

The agent-wrapper needs templates to copy to `agents/<agent>/queue/in/` when prompts are assigned. Templates provide standardized task files that reference `prompts/wip/prompt.md` and `README.1shot`.

## Tasks

### 1. Create Templates Directory

```bash
mkdir -p agents/templates
```

### 2. Create Default Template

**File:** `agents/templates/default.md`

```markdown
# Agent Task: {prompt_name}

## Assignment
- Agent: {agent_name}
- Model: {model}
- Started: {timestamp}

## Task Context

**Prompt File:** `prompts/wip/{prompt_filename}`
**Project Guide:** `README.1shot`

Read both files above for full context and guidelines.

## Task Description

{prompt_content}

## Work Log

PID: {pid}
Agent: {agent_name}
Model: {model}
Started: {timestamp}

---
### Agent work log (append steps below):

```

### 3. Create Template Documentation

**File:** `agents/templates/README.md`

```markdown
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
```

## Verification

```bash
# Verify template exists
ls -la agents/templates/
cat agents/templates/default.md
cat agents/templates/README.md

# Check placeholders are present
grep '{prompt_name}' agents/templates/default.md
grep '{agent_name}' agents/templates/default.md
```

## Completion Criteria

- [ ] `agents/templates/` directory created
- [ ] `default.md` template created with all 7 placeholders
- [ ] `README.md` documentation created
- [ ] All placeholders documented
- [ ] Files use UTF-8 encoding

