# Add Queue Mode Support to Wrapper Main

## Objective

Update the `main()` function in agent-wrapper to support `--queue-mode` flag and call template copy.

## Context

The wrapper's main() function needs to detect the `--queue-mode` flag and invoke template copying with proper variable substitution.

## Tasks

### 1. Update Usage Message

**File:** `bin/agent-wrapper`

**Around line 238, update usage check:**

```python
if len(sys.argv) < 6:
    log_message("Usage: agent-wrapper <prompt_filename> <agent_name> <model> <log_file> <wip_file> [--use-file <prompt_file>] [--queue-mode]")
    sys.exit(1)
```

### 2. Add Queue Mode Detection

**File:** `bin/agent-wrapper`

**After line 251 (after parsing arguments), add:**

```python
# Check for queue mode flag
queue_mode = "--queue-mode" in sys.argv
```

### 3. Add Template Copy Logic

**File:** `bin/agent-wrapper`

**After line 284 (after reading prompt_file content), add:**

```python
# If queue mode enabled, copy template to agent's queue/in/
if queue_mode:
    prompt_content = prompt_file.read_text(encoding='utf-8')
    template_vars = {
        'prompt_name': prompt_filename.replace('.md', '').replace('_', ' ').title(),
        'agent_name': agent_name,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'prompt_filename': prompt_filename,
        'prompt_content': prompt_content,
        'model': model,
        'pid': 'pending'
    }
    copy_template_to_queue(agent_name, prompt_filename, template_vars)
    log_message(f"Queue mode enabled - template copied for {agent_name}")
```

## Verification

```bash
# Check usage message updated
grep "Usage: agent-wrapper" bin/agent-wrapper | grep "queue-mode"

# Check queue mode detection
grep "queue_mode = \"--queue-mode\" in sys.argv" bin/agent-wrapper

# Check template copy call
grep "copy_template_to_queue(agent_name, prompt_filename, template_vars)" bin/agent-wrapper

# Verify all 7 template variables defined
grep -A 8 "template_vars = {" bin/agent-wrapper | grep -E "(prompt_name|agent_name|timestamp|prompt_filename|prompt_content|model|pid)"

# Test queue mode (dry run)
python3 bin/agent-wrapper test.md ollama-qwen codellama /tmp/test.log prompts/wip/test.md --use-file /tmp/prompt.txt --queue-mode 2>&1 | grep "Queue mode enabled"
```

## Completion Criteria

- [ ] Usage message includes `[--queue-mode]`
- [ ] Queue mode detection added: `queue_mode = "--queue-mode" in sys.argv`
- [ ] Template variables dictionary created with all 7 keys
- [ ] `copy_template_to_queue()` called when queue_mode is True
- [ ] Log message confirms queue mode enabled
- [ ] Code placed after prompt_file is read
- [ ] Template vars use proper formatting (title case for prompt_name, ISO timestamp)

1. Check usage message updated
2. Check queue_mode detection
3. Check template copy call
4. Check all 7 variables in template_vars
