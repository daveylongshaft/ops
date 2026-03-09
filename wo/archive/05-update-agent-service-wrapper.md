# Update Agent Service to Use New Wrapper

## Objective

Update the agent service to use `agent-wrapper` instead of `dc-agent-wrapper` and pass the `--queue-mode` flag.

## Context

The agent service (`packages/csc-shared/services/agent_service.py`) spawns the wrapper when prompts are assigned. It needs to use the new wrapper name and enable queue mode.

## Tasks

### 1. Update Wrapper Script Path

**File:** `packages/csc-shared/services/agent_service.py`

**Line 438, change:**

```python
# OLD:
wrapper_script = self.PROJECT_ROOT / "bin" / "dc-agent-wrapper"

# NEW:
wrapper_script = self.PROJECT_ROOT / "bin" / "agent-wrapper"
```

### 2. Add Queue Mode Flag to Wrapper Command

**File:** `packages/csc-shared/services/agent_service.py`

**Line 460-469, add `--queue-mode` after `str(prompt_file)`:**

```python
wrapper_cmd = [
    sys.executable if sys.executable else "python3",
    str( wrapper_script ),
    wip_path.name,
    agent_binary,
    model,
    str( log_file ),
    str( wip_path ),
    "--use-file",
    str( prompt_file ),
    "--queue-mode"  # NEW: Enable queue template copying
]
```

## Verification

```bash
# Check wrapper path updated
grep 'wrapper_script = self.PROJECT_ROOT / "bin" / "agent-wrapper"' packages/csc-shared/services/agent_service.py

# Check queue mode flag added
grep '"--queue-mode"' packages/csc-shared/services/agent_service.py

# Verify wrapper command structure
grep -A 12 "wrapper_cmd = \[" packages/csc-shared/services/agent_service.py | grep -E "(agent-wrapper|--queue-mode)"

# Test with actual agent assignment
agent list
agent select haiku
echo "# Test prompt" > prompts/ready/test-service-update.md
agent assign test-service-update.md

# Check if template was created
ls -la agents/haiku/queue/in/test-service-update.md
```

## Completion Criteria

- [ ] Line 438 uses `"agent-wrapper"` instead of `"dc-agent-wrapper"`
- [ ] Line 470 (new line) adds `"--queue-mode"` to wrapper_cmd list
- [ ] No syntax errors in wrapper_cmd list construction
- [ ] Agent assignment creates template in queue/in/
- [ ] Template contains substituted variables (not placeholders)

1. Check wrapper path updated
2. Check queue-mode flag added
3. Verify wrapper_cmd structure
