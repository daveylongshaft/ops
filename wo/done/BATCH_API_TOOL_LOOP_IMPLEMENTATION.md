# Batch API Tool Loop Implementation

**Purpose**: Build a reusable tool execution framework for Anthropic Batch API with proper tool_use/tool_result cycling

**Target**: Create infrastructure that can be invoked as:
```bash
claude_api_dir.sh /c/csc/batch_submissions/ --execute
```

---

## API Architecture Reference

### Batch API Tool Execution Flow

Per [Anthropic API Documentation - Tool Use](https://docs.anthropic.com/en/docs/build-a-claude-site-with-headers/tool-use):

**Tool Use in Messages API** (streaming/sync):
1. Client sends message with `tools` parameter
2. API returns `stop_reason: "tool_use"` with `ToolUseBlock` in content
3. Client executes tool locally
4. Client sends back `tool_result` with `tool_use_id` matching the call
5. API continues based on tool result

**Tool Use in Batch API** (async, fire-and-forget):
1. Client submits batch request with `tools` parameter
2. Batch processes asynchronously on Anthropic servers
3. API returns completed batch with `ToolUseBlock` in message content
4. **Client MUST**:
   - Retrieve batch results
   - Parse `ToolUseBlock` from responses
   - Execute tools **locally**
   - Create follow-up batch with `tool_result` blocks
   - Submit follow-up batch with `tool_use_id` references
   - Loop until `stop_reason: "end_turn"`

**Critical Difference**:
- Streaming API: Tools execute in real-time, blocking on results
- Batch API: Tools do NOT auto-execute; client must implement execution loop

---

## Data Structures

### ToolUseBlock (from batch results)

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

### Tool Result (client response)

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01GMcemxKcdJuHqJAq2ZEz3y",
  "content": "CSC Service Status\n================="
}
```

### Batch Request with Tools

```json
{
  "requests": [
    {
      "custom_id": "phase-1-stop-services",
      "params": {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 4096,
        "tools": [
          {
            "name": "run_command",
            "description": "Execute bash command",
            "input_schema": {
              "type": "object",
              "properties": {
                "command": {"type": "string"}
              },
              "required": ["command"]
            }
          }
        ],
        "system": "...",
        "messages": [{"role": "user", "content": "..."}]
      }
    }
  ]
}
```

---

## Implementation Specification

### Module: `batch_api_executor.py`

```python
class BatchAPIToolExecutor:
    """Execute batch requests with client-side tool handling."""

    def __init__(self, api_key, csc_root="/c/csc"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.csc_root = Path(csc_root)

    def submit_batch(self, requests: list) -> str:
        """Submit batch request, return batch ID."""
        batch = self.client.beta.messages.batches.create(requests=requests)
        return batch.id

    def retrieve_results(self, batch_id: str):
        """Retrieve all results from completed batch."""
        return self.client.beta.messages.batches.results(batch_id)

    def parse_tool_use(self, message) -> list:
        """Extract all ToolUseBlock from message."""
        tools = []
        for block in message.content:
            if block.type == "tool_use":
                tools.append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })
        return tools

    def execute_tool(self, name: str, input: dict) -> str:
        """Execute a tool locally and return result."""
        if name == "run_command":
            cmd = input["command"]
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result.stdout + result.stderr

        elif name == "read_file":
            path = input["path"]
            with open(path) as f:
                return f.read()

        elif name == "write_file":
            path = input["path"]
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(input["content"])
            return f"Written: {path}"

        elif name == "list_directory":
            return "\n".join(sorted(os.listdir(input["path"])))

        else:
            return f"Unknown tool: {name}"

    def execute_batch_with_loop(self, batch_id: str, max_iterations: int = 10):
        """Execute batch request with tool loop until completion."""
        messages = []

        for iteration in range(max_iterations):
            # Retrieve current batch results
            results = self.retrieve_results(batch_id)

            # Process results
            tool_results = []
            has_more_tools = False

            for result in results:
                if result.result.type == "succeeded":
                    message = result.result.message

                    # Print any text content
                    for block in message.content:
                        if block.type == "text":
                            print(f"[Claude] {block.text[:500]}")

                    # Execute tools
                    for block in message.content:
                        if block.type == "tool_use":
                            has_more_tools = True
                            print(f"[TOOL] {block.name}({block.input})...", flush=True)

                            output = self.execute_tool(block.name, block.input)
                            if len(output) > 2000:
                                output = output[:2000] + "\n...(truncated)"

                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": output
                            })

            # Check if done
            if not has_more_tools:
                print("\n[COMPLETE] No more tools to execute")
                break

            # Submit follow-up batch with tool results
            if tool_results:
                print(f"\n[SUBMIT] Resubmitting with {len(tool_results)} tool results...")

                followup_request = {
                    "custom_id": f"{batch_id}-followup-{iteration}",
                    "params": {
                        "model": "claude-haiku-4-5-20251001",
                        "max_tokens": 4096,
                        "messages": [
                            {"role": "user", "content": "[Original user message - implicit from batch]"},
                            {"role": "assistant", "content": "[Previous tool calls - implicit from batch]"},
                            {"role": "user", "content": tool_results}
                        ]
                    }
                }

                # This is simplified - real implementation needs to preserve full conversation
                # For now, we'd need to manually construct the message history

                # TODO: Implement proper follow-up batch submission
```

---

## Execution Flow Diagram

```
1. Submit Batch Request
   ↓
2. Wait for Batch Completion (status: "ended")
   ↓
3. Retrieve Results
   ↓
4. Parse ToolUseBlock from Response
   ↓
5. Execute Tool Locally
   ↓
6. Create tool_result with tool_use_id
   ↓
7. Submit Follow-up Batch with tool_result
   ↓
8. Loop back to Step 2
   ↓
9. Stop when stop_reason: "end_turn" (no more tool_use blocks)
```

---

## Implementation Checklist

- [ ] Create `batch_api_executor.py` with `BatchAPIToolExecutor` class
- [ ] Implement `submit_batch(requests)` method
- [ ] Implement `retrieve_results(batch_id)` method
- [ ] Implement `execute_tool(name, input)` for: run_command, read_file, write_file, list_directory
- [ ] Implement `execute_batch_with_loop(batch_id)` with proper message reconstruction
- [ ] Create CLI wrapper `claude_api.py` with argparse
- [ ] Create shell wrapper `claude_api.sh` / `claude_api.bat`
- [ ] Test with simple batch request
- [ ] Test with CSC restructure batch (ACTUAL WORK)
- [ ] Verify /c/csc/ restructured with irc/ and ops/ folders
- [ ] Verify all services running post-restructure

---

## Sample Tool Calls from Batch Results

### Phase 1 - Stop Services

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

Expected result:
```
CSC Service Status
========================================
  queue-worker         enabled
  test-runner          enabled
  pm                   enabled
  server               enabled
  bridge               enabled

Clients:
  gemini               enabled
```

### Phase 2 - Restructure

Multiple tool calls expected:
- `run_command`: `git status`, `mkdir`, `cp`, etc.
- `read_file`: Read existing files for context
- `write_file`: Create new files, update paths
- `list_directory`: Verify structure changes

### Phase 3-5

Similar pattern: Execute commands, verify results, continue

---

## Cost Optimization

**Batch API Cost Model**:
- No streaming overhead
- Tools executed client-side (no API cost for execution)
- Follow-up batches with tool_result blocks (cheaper than streaming equivalent)

**For CSC Restructure**:
- ~5 phases × ~2-3 tool calls per phase = ~12 total tool submissions
- System context cached (95% savings after first request)
- Estimated cost: ~$0.02 total (Haiku at $0.80/MTok in, $4/MTok out)

---

## Next Steps

1. Implement `batch_api_executor.py` with full tool execution loop
2. Test with existing batch IDs: msgbatch_01JoDGSYgfqHBQqMXh9jnUaK, etc.
3. Execute Phase 1-5 tool calls sequentially
4. Verify /c/csc/ restructure complete
5. Confirm all services running
6. Document final state
