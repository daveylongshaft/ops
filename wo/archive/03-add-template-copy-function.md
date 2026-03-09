# Add Template Copy Function to Wrapper

## Objective

Add `copy_template_to_queue()` function to the agent-wrapper for template-based queue integration.

## Context

The wrapper needs to copy templates from `agents/templates/default.md` to `agents/<agent>/queue/in/` with variable substitution when `--queue-mode` flag is used.

## Tasks

### 1. Add Template Copy Function

**File:** `bin/agent-wrapper`

**Insert after line 102 (after `move_prompt()` function):**

```python
def copy_template_to_queue(agent_name, prompt_filename, template_vars):
    """Copy template to agent's queue/in/ directory with variable substitution.

    Args:
        agent_name: Name of the agent (e.g., "ollama-qwen")
        prompt_filename: Name of the prompt file (e.g., "task.md")
        template_vars: Dictionary of variables to substitute in template

    Returns:
        bool: True if template copied successfully, False otherwise
    """
    template_file = CSC_ROOT / "agents" / "templates" / "default.md"

    if not template_file.exists():
        log_message(f"WARNING: Template not found at {template_file}, skipping queue copy")
        return False

    try:
        # Read template
        template_content = template_file.read_text(encoding='utf-8')

        # Substitute variables
        for key, value in template_vars.items():
            placeholder = f"{{{key}}}"
            template_content = template_content.replace(placeholder, str(value))

        # Write to queue/in/
        queue_in_dir = CSC_ROOT / "agents" / agent_name / "queue" / "in"
        queue_in_dir.mkdir(parents=True, exist_ok=True)

        queue_file = queue_in_dir / prompt_filename
        queue_file.write_text(template_content, encoding='utf-8')

        log_message(f"Copied template to {agent_name}/queue/in/{prompt_filename}")
        return True

    except Exception as e:
        log_message(f"ERROR: Failed to copy template: {e}")
        return False
```

## Verification

```bash
# Verify function exists
grep -A 30 "def copy_template_to_queue" bin/agent-wrapper

# Check function signature
grep "copy_template_to_queue(agent_name, prompt_filename, template_vars)" bin/agent-wrapper

# Verify error handling
grep "try:" bin/agent-wrapper | grep -A 5 "copy_template"

# Count lines (should be ~40 new lines)
wc -l bin/agent-wrapper
```

## Completion Criteria

- [ ] Function `copy_template_to_queue()` added after line 102
- [ ] Function has docstring with Args and Returns
- [ ] Template file path uses `CSC_ROOT / "agents" / "templates" / "default.md"`
- [ ] Variable substitution loop implemented
- [ ] Queue directory created with `mkdir(parents=True, exist_ok=True)`
- [ ] UTF-8 encoding used for read/write
- [ ] Error handling with try/except
- [ ] Success/failure logged with `log_message()`
- [ ] Returns boolean for success/failure

1. Check copy_template_to_queue function exists
2. Verify function has docstring
3. Check error handling
4. Verify returns boolean
