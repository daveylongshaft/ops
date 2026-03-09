# Implement Prompt Caching for Anthropic Agents

## Summary

Build full implementation of Anthropic API prompt caching for all Anthropic model agents
(haiku, sonnet, opus, claude) launched by queue-worker. Only applies to Anthropic models -
Gemini and local agents are unaffected.

## Background Research (Completed)

Full investigation of Claude API prompt caching was done. Key findings:

### How It Works
- `cache_control: {"type": "ephemeral"}` on system/tools blocks
- Cache TTL: 5 minutes (default) or 1 hour (2x write cost)
- Cache reads cost **0.1x** normal input token price (90% savings)
- Cache writes cost 1.25x (slight premium on first call)
- Minimum cacheable size: 1,024 tokens (Sonnet), 4,096 tokens (Opus/Haiku 4.5)
- Max 4 cache breakpoints per request
- Exact byte-match required for cache hits

### API Call Structure for Caching
```python
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=4096,
    system=[{
        "type": "text",
        "text": "static system instructions...",
        "cache_control": {"type": "ephemeral"}
    }],
    messages=[
        {"role": "user", "content": "dynamic task reference only"}
    ]
)
```

### Cost Comparison
| Component | Tokens (est.) | Without Cache | With Cache (hit) |
|---|---|---|---|
| Tools definitions | ~2,000 | 1.0x | 0.1x |
| System prompt | ~500 | 1.0x | 0.1x |
| User message | ~50 | 1.0x | 1.0x |
| **Total effective** | **~2,550** | **~2,550** | **~300** |

Current approach inlines ~10,000+ tokens (README.1shot + context files + WIP content)
every single call. With caching + file references, drops to ~300 effective tokens after
first call.

## Architecture Decision

### Current (Bad)
`build_full_prompt()` reads and INLINES all file contents into one giant prompt_text
string passed as the user message to cagent. Every invocation pays full token cost for
all of it.

### Target (Good)
- **cagent.yaml `instruction`** (system prompt) = STATIC, CACHEABLE per agent
  - Contains README.1shot procedures as file references ("Read README.1shot")
  - References tools/INDEX.txt, tree.txt, p-files.list as paths to read
  - References agents/<name>/context/*.md as paths
  - Contains journaling rules and DO NOT rules (static text)
  - Identical across all invocations of the same agent = perfect cache hits

- **orders.md / prompt_text** (user message) = TINY, only variable is filename
  - Just: "Your task is workorders/wip/{prompt_filename}. Read it and begin."
  - Agent uses filesystem tools to read the actual workorder at runtime

- Agent reads files on demand using its filesystem tools (read_file, shell)
  - Only reads what it actually needs for the task
  - Always gets live/current file contents (no stale inlined context)

## Implementation Tasks

### 1. Update cagent.yaml per agent
Move real instructions into `instruction` field with file references:
```yaml
instruction: |
  You are a one-shot focused agent. Follow these procedures:

  ## Setup
  1. Read README.1shot for full workflow procedures
  2. Read tools/INDEX.txt for the code map
  3. Read tree.txt for directory structure
  4. Read your task file (provided in the user message)

  ## Agent Context
  Read these for agent-specific guidelines:
  - agents/{agent_name}/context/project-map.md
  - agents/{agent_name}/context/test-guidelines.md

  ## Rules
  - Journal EVERY step to the WIP file BEFORE doing it
  - Do NOT touch git, move files, or run tests
  - When done, echo "COMPLETE" to the WIP file and exit
```

### 2. Simplify build_full_prompt()
```python
def build_full_prompt(agent_name, prompt_filename):
    """Just return the task reference. Context is in cagent.yaml instruction."""
    return f"Your task file is: workorders/wip/{prompt_filename}\nRead it and begin."
```

### 3. Simplify agents/templates/default.md
```markdown
Your task file is: workorders/wip/{prompt_filename}
Read it, understand it, do the work, journal to it, echo COMPLETE when done.
```

### 4. Verify cagent supports cache_control
- Check if cagent passes `cache_control` to Anthropic API
- If not: add `cache_control` key to YAML config that cagent passes through
- Or if cagent uses recent Anthropic SDK, check for top-level cache_control support
- Fallback: fork cagent or bypass with direct SDK calls from queue_worker.py

### 5. Add cache_control to cagent.yaml models section
```yaml
models:
  anthropic/claude-haiku-4-5-20251001:
    provider: anthropic
    model: claude-haiku-4-5-20251001
    temperature: 0.3
    max_tokens: 4096
    cache_control:
      type: ephemeral
```

### 6. Monitor cache performance
Log `cache_read_input_tokens` and `cache_creation_input_tokens` from API responses
to verify caching is working and measure actual savings.

## Scope
- **IN SCOPE**: haiku, sonnet, opus, claude agents (Anthropic API)
- **OUT OF SCOPE**: gemini*, chatgpt, codellama, deepseek, qwen (different APIs)
- **OUT OF SCOPE**: Changing how non-Anthropic agents work

## Dependencies
- Queue-worker must be functional (bin/workorders, bin/agent verified)
- cagent binary must support cache_control or be replaceable

## Work Log

PID: 46040 agent: opus starting at 2026-02-25 12:39:54

PID: 28056 agent: opus starting at 2026-02-25 19:50:56


--- AUDIT [2026-02-27 13:22] ---
INCOMPLETE
Pending:
  - No work log entries showing actual implementation steps taken
  - Work log only shows PID lines with no description of actions performed
  - No evidence that cagent.yaml files were actually updated per agent
  - No verification that build_full_prompt() was simplified
  - No confirmation that agents/templates/default.md was modified
  - No evidence that cagent cache_control support was checked or implemented
  - No logs showing cache_control was added to YAML configuration
  - No monitoring/testing results showing cache performance was verified
  - Missing 'COMPLETE' marker in work log
  - No actual code changes, file modifications, or testing documented
This is a planning/architecture document with excellent design specifications but NO evidence of implementation work - just PID log lines with no actual task execution recorded.


DEAD END - Prompt caching implemented in run_agent.py via --system-prompt (2026-02-27)
