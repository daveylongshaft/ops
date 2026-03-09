# Build Batch API Tool Executor with Proper Tool Loop

**Agent**: Opus
**Priority**: P0
**Scope**: Implement production-grade Batch API tool execution framework
**Test Case**: Execute pending CSC restructure batches

---

## Context: What We Know

### Batch IDs (Already Submitted, Awaiting Execution)

```
Phase 1: msgbatch_01JoDGSYgfqHBQqMXh9jnUaK (Stop & Uninstall)
Phase 2: msgbatch_01MEAQxvNL69HAbPDYsuaeR3 (Execute Restructure)
Phase 3: msgbatch_01YENeceG7qXCu6WaVu9VxXs (Reinstall & Verify)
Phase 4: msgbatch_01VR2ZAWYhvXFtgovqYmy88H (Start Services)
Phase 5: msgbatch_01HTVWVLazaYVfL7Lg8BeiAu (Final Verification)
```

### Sample Tool Call from Batch Results

```json
{
  "type": "tool_use",
  "id": "toolu_01GMcemxKcdJuHqJAq2ZEz3y",
  "name": "run_command",
  "input": {
    "command": "csc-ctl status"
  }
}
```

### Available Tools (Defined in Batch Requests)

1. **run_command**: Execute bash commands
2. **read_file**: Read file contents
3. **write_file**: Write/create files
4. **list_directory**: List directory contents

---

## Task: Build Complete Tool Executor

### Module: `/c/csc/bin/batch_executor.py`

Build a production-grade executor that:

1. **Retrieves batch results** from provided batch IDs
2. **Parses tool_use blocks** from Claude's responses
3. **Executes tools locally**:
   - `run_command`: Execute bash, capture output
   - `read_file`: Read file, return content
   - `write_file`: Create/update files
   - `list_directory`: List directory contents
4. **Creates tool_result blocks** with proper `tool_use_id` reference
5. **Handles follow-up batches** (resubmitting with tool results)
6. **Implements retry loop** (continue until `stop_reason: "end_turn"`)
7. **Logs all operations** for debugging/auditing

### Architecture

```
main()
  ├─ Load API key from .env
  ├─ Initialize Anthropic client
  ├─ For each batch_id:
  │   ├─ retrieve_batch_results(batch_id)
  │   ├─ parse_tool_use_blocks(results)
  │   ├─ For each tool_use:
  │   │   ├─ execute_tool_locally()
  │   │   └─ collect tool_result
  │   ├─ If has_more_tools:
  │   │   └─ submit_followup_batch(tool_results)
  │   └─ Loop until stop_reason = "end_turn"
  └─ Report completion
```

### Key Implementation Details

**Batch Result Structure** (from API docs):
```python
# Results from client.beta.messages.batches.results(batch_id)
result.result.type == "succeeded"  # or "expired", "failed", "errored"
result.result.message.content[]  # Array of content blocks
  - type: "text" -> text.text
  - type: "tool_use" -> tool_use.{id, name, input}
```

**Tool Execution** (client-side):
```python
# Execute tool locally based on tool_use block
if tool_use.name == "run_command":
    output = subprocess.run(tool_use.input["command"], ...)

# Package result
tool_result = {
    "type": "tool_result",
    "tool_use_id": tool_use.id,  # CRITICAL: must match tool_use.id
    "content": output
}
```

**Follow-up Batch** (resubmit with results):
```json
{
  "requests": [
    {
      "custom_id": "phase-1-followup-1",
      "params": {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 4096,
        "messages": [
          {
            "role": "user",
            "content": [tool_result, tool_result, ...]  // Array of results
          }
        ]
      }
    }
  ]
}
```

---

## Implementation Checklist

### Phase 1: Core Executor
- [ ] Create `batch_executor.py` with `BatchAPIExecutor` class
- [ ] Implement `__init__(api_key, log_dir)`
- [ ] Implement `retrieve_results(batch_id)` -> list of results
- [ ] Implement `parse_tool_uses(result)` -> list of tool_use dicts
- [ ] Implement tool execution methods:
  - [ ] `_exec_run_command(command)` -> str
  - [ ] `_exec_read_file(path)` -> str
  - [ ] `_exec_write_file(path, content)` -> str
  - [ ] `_exec_list_directory(path)` -> str
- [ ] Implement `execute_tool(tool_name, input)` dispatcher
- [ ] Add comprehensive error handling + logging

### Phase 2: Batch Loop
- [ ] Implement `execute_batch_with_loop(batch_id, max_iterations=10)`
- [ ] Loop logic:
  1. Retrieve batch results
  2. Parse all tool_use blocks
  3. Execute all tools, collect tool_results
  4. If `stop_reason == "end_turn"`: STOP
  5. If tools pending: submit follow-up batch
  6. Continue loop
- [ ] Handle edge cases (timeouts, errors, retries)

### Phase 3: CLI & Testing
- [ ] Implement `main()` CLI entry point
- [ ] Arguments: `--batch-id <id>` or `--batch-ids <id1> <id2> ...`
- [ ] Options: `--log-dir`, `--max-iterations`, `--dry-run`
- [ ] Test with actual batch IDs:
  ```bash
  python /c/csc/bin/batch_executor.py --batch-id msgbatch_01JoDGSYgfqHBQqMXh9jnUaK
  ```

### Phase 4: Documentation
- [ ] Write docstrings for all methods
- [ ] Document tool execution behavior
- [ ] Document error handling strategy
- [ ] Document log output format

---

## Test Case: CSC Restructure Batches

**Use the 5 submitted batches to test the executor:**

1. Start with Phase 1 batch (simple: csc-ctl status)
2. Progress through Phase 2-5
3. Verify final state: `/c/csc/irc/packages`, `/c/csc/ops/wo` exist

**Success criteria:**
- All 5 batches execute completely
- All tool calls execute without errors
- `/c/csc/` restructured: irc/ and ops/ populated
- Backup created: `/c/csc_old/`

---

## Output

Produce:
1. `/c/csc/bin/batch_executor.py` - Main executor module
2. `/c/csc/bin/batch_executor_test.py` - Test harness with actual batch IDs
3. `/c/csc/docs/batch_api_tool_loop.md` - Architecture documentation

---

## Success Definition

When complete:
- [ ] `python /c/csc/bin/batch_executor.py --batch-ids msgbatch_01JoDGSYgfqHBQqMXh9jnUaK msgbatch_01MEAQxvNL69HAbPDYsuaeR3 ...` executes all 5 batches
- [ ] All tool calls from batches are executed locally
- [ ] `/c/csc/` is fully restructured with new irc/ and ops/ folders
- [ ] `/c/csc_old/` contains backup of original structure
- [ ] Zero manual intervention needed after script starts
