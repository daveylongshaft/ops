---
urgency: P2
agent: haiku
requires: markdown,documentation
tags: docs,reference,user-guide
blockedBy: gemini-api-workflows-00-skeleton.md,gemini-api-workflows-08-queue.md
---

# Workorder: Gemini Batch API - Documentation

## Context
Create comprehensive documentation for the Gemini batch pipeline. Two files: detailed reference guide + GEMINI.md update linking to it.

**Related:** Part 11 of 12-part series. Blocked by workorders 00 & 08. Unblocks public-facing usage.

## Deliverables

### Create `docs/gemini-batch-api.md`

**Table of Contents:**
1. Overview & Modes
2. Quick Start (3 modes)
3. Built-in Tools
4. Context Caching
5. Cost Estimation
6. CLI Reference
7. Configuration
8. Error Handling
9. Examples
10. Troubleshooting

### 1. Overview & Modes Section
**Content:**
- One-paragraph summary: "Gemini batch API integration for CSC workorder processing"
- Three execution modes:

| Mode | API Type | Speed | Cost | Tools | Use Case |
|------|----------|-------|------|-------|----------|
| **Batch API** | Google Batches | Async (1-2 min) | 50% off | None (text-only) | Summarization, code review, docs |
| **Tool Loop** | generate_content | Sync (1-5 min) | Standard | Custom + built-in | Implementation, file I/O, shell commands |
| **Queue Worker** | Pipeline | Async per job | 50% off + cache | Auto-selected | Continuous automation, scheduled runs |

**Constraint Note:**
- Built-in tools (google_search, code_execution) conflict with custom tools on Gemini 3.x
- Each request chooses one: custom tools XOR built-in tools

### 2. Quick Start: Three Modes

**A. Batch API Mode (Text-Only, 50% Off)**
```bash
# Add workorder to batch config
gbatch_add.py workorders/gemini-api/sample.md --model gemini-2.5-flash

# Submit batch (async)
gbatch_run.py run bin/gemini-batch/batch_config.json --agent gemini

# Check status
gbatch_run.py status <job_name>

# Retrieve results when done
gbatch_run.py retrieve <job_name>
```

**B. Tool Loop Mode (Full Power, Sync)**
```bash
# Single workorder
gbatch_tool_run.py workorders/gemini-api/sample.md --model gemini-2.5-flash

# Batch with parallelism
gbatch_tool_run.py batch bin/gemini-batch/batch_config.json --parallel 4

# With built-in code execution
gbatch_tool_run.py workorders/gemini-api/sample.md --builtin code_execution
```

**C. Queue Worker Mode (Continuous, Automated)**
```bash
# Set up queue processor
csc-ctl config queue-worker enabled true

# Or run manually
gbatch_queue_run.py --agent gemini --max-cycles 10

# Check progress
agent tail 50
```

### 3. Built-in Tools Section
**Content:**
- **google_search** — Search web, get grounded results with citations
  - Automatically included in responses as grounding metadata
  - No explicit "tool call" — model integrates search naturally
  - Example: "What are the latest developments in AI?"

- **code_execution** — Execute Python code in sandbox
  - Run code and get output directly in response
  - Useful for math, data analysis, verification
  - Example: "Calculate the sum of 1 to 100"

**Conflict Note:**
- Cannot use google_search + code_execution together with custom tools
- If workorder needs file I/O: use custom tools (no built-in)
- If workorder needs web search: use `--builtin google_search` (no custom tools)

### 4. Context Caching Section
**Content:**
- What it caches: CLAUDE.md + GEMINI.md + tools/INDEX.txt + tree.txt
- How much: ~4,500 tokens ≈ 90% input token savings per request
- Cost: $0.015/M input cached (vs $0.15/M normal) = 10x cheaper per cached token

**Setup:**
```bash
# Create cache
gbatch_cache.py create --model gemini-2.5-flash --ttl 3600

# Use in batch
gbatch_run.py run batch_config.json --cache

# Or in tool-loop
gbatch_tool_run.py sample.md --cache

# List caches
gbatch_cache.py list

# Refresh expiring cache
gbatch_cache.py refresh <cache_name> --ttl 7200
```

**Cost Example:**
- Without cache: 100 requests × 2,000 avg input tokens = $0.30
- With cache: 100 requests × 500 uncached tokens = $0.075 + cache creation cost ≈ $0.08 total
- **Savings: 73% on input tokens** (better ROI on larger batches)

### 5. Cost Estimation Section
**Content:**
- Model pricing (Gemini 2.5 Flash vs Pro)
- Batch API discount: 50% off output tokens
- Cache discount: 90% off cached input, cache creation ≈ $0.01-0.02
- Token counting: how to estimate before running

**Pricing Table:**
```
Gemini 2.5 Flash:
  Input:  $0.075 / 1M tokens
  Output: $0.30 / 1M tokens
  Batch API: 50% discount on output → $0.15 / 1M output
  Cache hit: $0.0075 / 1M cached input, $0.30 / 1M cache creation

Gemini 2.5 Pro:
  Input:  $1.50 / 1M tokens
  Output: $6.00 / 1M tokens
  Batch API: 50% discount → $3.00 / 1M output
```

**Example Costs:**
1. Batch API: 1,000 input + 500 output tokens
   - Cost: (1,000 × $0.075 + 500 × $0.15) / 1M = $0.00008 ≈ $0.00008
2. Tool Loop: 2,000 input (with 1,500 cached) + 800 output
   - Cost: (500 × $0.075 + 1,500 × $0.0075 + 800 × $0.30) / 1M ≈ $0.00029
   - Savings vs uncached: 73%

### 6. CLI Reference
**Detailed subcommand docs:**

```bash
gbatch_add.py <workorder> [--model] [--agent] [--tools]
gbatch_list.py [--provider] [--model] [--summary]
gbatch_edit.py <entry> [--model] [--tools] [--agent]
gbatch_remove.py <entry> [--force]

gbatch_convert.py to-jsonl <file.md> [--model] [--out]
gbatch_convert.py from-results <results.jsonl> [--out]
gbatch_convert.py batch to-jsonl <dir/> [--out]

gbatch_run.py submit <requests.jsonl> [--model] [--cache]
gbatch_run.py status <job_name>
gbatch_run.py retrieve <job_name> [--out]
gbatch_run.py run <config.json> [--agent] [--cache] [--async]

gbatch_tool_run.py <workorder.md> [--model] [--cache] [--builtin]
gbatch_tool_run.py batch <config.json> [--agent] [--parallel] [--defer-git-sync]

gbatch_cache.py create [--model] [--ttl] [--name]
gbatch_cache.py list
gbatch_cache.py delete <name>
gbatch_cache.py refresh <name> [--ttl]
gbatch_cache.py stats

gbatch_queue_run.py [--config] [--agent] [--max-cycles] [--mode]
```

(Include full option descriptions and examples)

### 7. Configuration Section
**Content:**
- Format of `batch_config.json` entries
- YAML frontmatter in workorders (model, requires, tools, urgency)
- Environment variables (GOOGLE_API_KEY, CSC_WIP_FILE, CSC_BATCH_DEFER_GIT_SYNC)

**Example config entry:**
```json
{
  "id": "entry-20260303-abc123",
  "workorder": "workorders/gemini-api/sample.md",
  "model": "gemini-2.5-flash",
  "agent": "gemini",
  "provider": "gemini",
  "builtin_tools": [],
  "added_at": "2026-03-03T12:00:00Z"
}
```

**Example workorder frontmatter:**
```yaml
---
urgency: P2
agent: gemini
model: gemini-2.5-pro
requires: [file_io, shell]
builtin_tools: []
---
```

### 8. Error Handling Section
**Content:**
- Common errors + solutions
- Rate limits and backoff strategy
- Network timeouts
- Malformed workorders
- Missing API key

**Table:**
| Error | Cause | Solution |
|-------|-------|----------|
| `API key not found` | GOOGLE_API_KEY not set | Set env var or config file |
| `QUOTA_EXCEEDED` | Hit rate limit | Wait 60s, retry with backoff |
| `JSONL validation failed` | Bad request format | Check converter output |
| `Function call unknown` | Custom tool doesn't exist | Check tool declarations |

### 9. Examples Section
**Content:**
- End-to-end workflow: add → run → check → retrieve
- Batch processing multiple workorders
- Cost-optimized workflow (cache + batch API)
- Error recovery

**Full Example:**
```bash
# 1. Add 3 workorders to batch
gbatch_add.py workorders/gemini-api/task1.md --model gemini-2.5-flash
gbatch_add.py workorders/gemini-api/task2.md --model gemini-2.5-flash
gbatch_add.py workorders/gemini-api/task3.md --model gemini-2.5-pro

# 2. Create cache (optional)
gbatch_cache.py create --model gemini-2.5-flash --ttl 3600

# 3. Run batch
gbatch_run.py run bin/gemini-batch/batch_config.json --cache
# Output: Submitted batch batchOperations/abc123 with 3 requests. Model: gemini-2.5-flash.

# 4. Check status
gbatch_run.py status batchOperations/abc123
# Output: QUEUED, 0/3 completed. ETA: 2 minutes.

# 5. Retrieve when done
gbatch_run.py retrieve batchOperations/abc123 --out results.jsonl
# Output: Retrieved 3 results. 3 succeeded, 0 failed. Cost: $0.00024

# 6. Convert results to markdown
gbatch_convert.py from-results results.jsonl --out summary.md
```

### 10. Troubleshooting Section
**Content:**
- Why is my batch still queued?
- How do I force a retry?
- Can I use custom tools with google_search?
- What if a workorder times out?
- How do I debug tool loop execution?

---

### Update `GEMINI.md`

**Add new section (after existing content):**

```markdown
## Batch Pipeline

CSC includes a full Gemini batch processing pipeline in `bin/gemini-batch/`, mirroring the Anthropic batch infrastructure.

**Key Features:**
- Two modes: async batch API (50% off) or sync tool-loop (full file I/O)
- Built-in tools: google_search, code_execution
- Context caching: 90% input token savings
- Queue-worker integration: continuous automation
- Cost-optimized: batch discounts + cache combined

**Quick Start:**
```bash
# Add workorder
gbatch_add.py workorders/my-task.md --model gemini-2.5-flash

# Run (choose one mode)
gbatch_run.py run batch_config.json        # Async batch (50% off)
gbatch_tool_run.py batch batch_config.json # Sync with tools
gbatch_queue_run.py                        # Continuous queue

# Check progress
agent tail
```

**Full Documentation:** See `docs/gemini-batch-api.md`

**Cost Estimate:** With batch discounts + caching, Gemini batch jobs typically cost 70-80% less than real-time API calls. See pricing section in docs.
```

---

## Testing Notes
- Verify all code examples in docs are syntactically correct (can be parsed)
- Verify all file paths are relative to `/c/csc/`
- Verify all command examples have expected output comments
- Verify pricing calculations are accurate

## Notes
- Docs should be accessible to non-technical CSC users
- All examples are copy-paste ready
- Pricing section uses realistic token counts and model rates
- Link from GEMINI.md to full docs in git
