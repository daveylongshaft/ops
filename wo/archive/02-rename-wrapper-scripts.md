# Rename Wrapper Scripts

## Objective

Rename `dc-agent-wrapper` to `agent-wrapper` to reflect its universal purpose (not just docker-coder).

## Context

The `dc-agent-wrapper` was originally designed for docker-coder but is now used for all agents (cloud, local, docker tools). Rename it to `agent-wrapper`.

## Tasks

### 1. Copy Python Script

```bash
cp bin/dc-agent-wrapper bin/agent-wrapper
chmod +x bin/agent-wrapper
```

### 2. Copy Windows Batch Wrapper

```bash
cp bin/dc-agent-wrapper.bat bin/agent-wrapper.bat
```

### 3. Update Batch File Reference

**File:** `bin/agent-wrapper.bat`

**Change line 2:**
```batch
@echo off
python "%~dp0agent-wrapper" %*
```

### 4. Update Script Docstring

**File:** `bin/agent-wrapper`

**Update header (lines 1-26):**
- Change all references from `dc-agent-wrapper` to `agent-wrapper`
- Update usage examples:
  ```
  Usage:
      agent-wrapper <prompt_filename> <agent_name> <model> <log_file> <wip_file> [--use-file <prompt_file>] [--queue-mode]

  Examples:
      agent-wrapper task.md ollama-agent codellama:7b /tmp/log.txt /path/wip/task.md
      agent-wrapper task.md claude sonnet /tmp/log.txt /path/wip/task.md --queue-mode
  ```

### 5. Update log_message Function

**File:** `bin/agent-wrapper` (line 47)

**Change:**
```python
def log_message(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [agent-wrapper] {message}")
```

## Verification

```bash
# Verify new files exist
ls -la bin/agent-wrapper
ls -la bin/agent-wrapper.bat

# Verify execute permission (Unix)
test -x bin/agent-wrapper && echo "Executable" || echo "Not executable"

# Check docstring updated
head -26 bin/agent-wrapper | grep "agent-wrapper"

# Verify old wrapper still exists (backward compatibility)
ls -la bin/dc-agent-wrapper
```

## Completion Criteria

- [ ] `bin/agent-wrapper` created (copy of dc-agent-wrapper)
- [ ] `bin/agent-wrapper.bat` created and updated
- [ ] Execute permissions set on Unix
- [ ] Docstring updated with new name
- [ ] Usage examples include `--queue-mode` flag
- [ ] log_message uses "[agent-wrapper]" prefix
- [ ] Old `dc-agent-wrapper` still exists for backward compatibility

1. Checking if agent-wrapper exists
2. Checking execute permissions
3. Checking docstring updated
4. Checking batch file updated
PID: 28332 agent: ollama-qwen starting at 2026-02-21 01:20:44
