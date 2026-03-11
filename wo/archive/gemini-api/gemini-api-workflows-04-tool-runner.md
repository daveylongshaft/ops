---
urgency: P2
agent: sonnet
requires: python,google-genai,tool-execution
tags: tool-loop,sync,implementation
blockedBy: gemini-api-workflows-02-tools.md
---

# Workorder: Gemini Batch API - Synchronous Tool-Loop Runner

## Context
Implement the synchronous tool-execution path for Gemini. This is the full power mode: API calls tool, executes custom tools, feeds results back, repeats. Equivalent to the existing Gemini CLI integration but via Python SDK with full Claude Code tools support.

**Related:** Part 5 of 12-part series. Blocked by workorder 02. Unblocks workorder 08.

## Deliverables

### Create `bin/gemini-batch/gbatch_tool_run.py`

**CLI Usage:**
```
gbatch_tool_run.py <workorder.md> [--model gemini-2.5-flash] [--cache]
                    [--builtin code_execution,google_search]
gbatch_tool_run.py batch <batch_config.json> [--agent gemini] [--parallel 4]
                    [--defer-git-sync]
```

### 1. Single Workorder Mode
**Process:**
1. Parse `.md` file YAML frontmatter (extract model, builtin tools)
2. CLI overrides: `--model` overrides frontmatter
3. Get Gemini API key via `common.get_gemini_api_key()`
4. Load system context via `common.load_system_context([...])`
5. Format workorder content (strip frontmatter) via `common.format_workorder(path)`
6. Initialize tools:
   - Create `ToolExecutor` from workorder 02
   - If `--builtin` specified: add built-in tools from workorder 06
   - Validate: **custom tools and built-in tools conflict on Gemini 3.x**
     - If both requested: print clear error: `"ERROR: Cannot use custom tools and built-in tools together on Gemini 3.x. Choose one mode."`
     - Exit with status 1
7. Create client and call tool loop:
   ```python
   client = google.genai.Client(api_key=key)
   result = executor.run_tool_loop(
       client=client,
       model=model_name,
       system_text=system_context,
       prompt=workorder_content,
       max_rounds=20
   )
   ```
8. Print result + token usage to stdout
9. If journal file path detected (env var `CSC_WIP_FILE`): append to journal with timestamp
   ```
   [COMPLETE] Tool loop finished. Final answer: <first 200 chars>
   Token usage: input=<N>, output=<M>, cost=$<X>
   ```
10. Exit with status 0 (success) or 1 (error)

**Output:**
- Stdout: Final answer from model
- Stderr: Logs of each tool call and round

### 2. Batch Mode
**Process:**
1. Load `batch_config.json` via `common.load_config(path)`
2. Filter entries with `"provider": "gemini"`
3. For each entry:
   - Extract workorder file path, model, builtin tools
   - Create WIP journal file (if `CSC_WIP_FILE` env var set)
   - Call single workorder logic above
   - On success: append result to journal
   - On failure: log error, continue (partial batch completion)
4. If `--parallel N`: Use ThreadPoolExecutor with N workers to process entries in parallel
   - Each thread has its own client (API key reused)
   - Print progress: `"[1/10] Processing <workorder> ... DONE"`
5. Summary:
   - N completed, N failed
   - Total tokens, total cost
6. If `--defer-git-sync`: do NOT run `git add + commit` at end
   - Set `CSC_BATCH_DEFER_GIT_SYNC=1` as env var for queue-worker to pick up
   - Otherwise: run git sync at end (existing agent-wrapper pattern)

### 3. Tool-Loop Integration with `ToolExecutor`
Validate that `ToolExecutor.run_tool_loop()` from workorder 02:
- Accepts `client`, `model`, `system_text`, `prompt`, `max_rounds`
- Returns final text answer (string)
- Logs each round to stdout
- Handles timeouts and max rounds gracefully

### 4. Built-in Tool Support
Import from workorder 06:
- `GoogleSearchTool.get_tool()` → adds google_search capability
- `CodeExecutionTool.get_tool()` → adds code_execution capability
- Cannot use both custom tools AND built-in tools simultaneously

**Parsing `--builtin` flag:**
- `--builtin code_execution` → only code execution
- `--builtin google_search` → only search
- `--builtin code_execution,google_search` → error (conflict with custom)
- Default (no flag): use custom tools only

### 5. Cache Support
If `--cache` flag:
- Call `CacheManager.get_active(model)` from workorder 07
- If valid cached content name: embed in request as `cached_content` (per Gemini API)
- Track cache hit/miss in output

### 6. Error Handling
- Missing workorder file: print error, skip (batch mode) or exit (single mode)
- Invalid YAML: print error with line number, skip
- API key missing: clear error pointing to env var setup
- Tool execution timeout: return `"TIMEOUT"` and continue (don't crash loop)
- Max rounds exceeded: return partial answer or error message
- Network errors: retry up to 3 times, then fail entry

### 7. Journal Integration
If `CSC_WIP_FILE` env var is set (set by queue-worker):
- Append each major milestone:
  ```
  [12:34:56] Starting tool loop...
  [12:34:57] Round 1: Calling read_file(/c/csc/file.py)
  [12:34:58] Round 1: Result: <first 100 chars>...
  [12:35:10] Round 2: Calling write_file(...)
  [12:35:15] COMPLETE: Final answer in 3 rounds
  Token usage: input=5234, output=1456, cache_read=1024
  Cost: $0.015 (with cache)
  ```

## Testing Notes
- Unit test: `test_tool_run_single_workorder()` — mock workorder, mock tool executor, verify output
- Unit test: `test_tool_run_builtin_conflict()` — request both custom + builtin tools, verify error
- Unit test: `test_tool_run_batch_parallel()` — mock 3 workorders, --parallel 2, verify concurrent execution
- Unit test: `test_tool_run_cache_hit()` — mock cached content, verify cache name embedded
- Unit test: `test_tool_run_journal_append()` — set CSC_WIP_FILE, verify journal written

## Notes
- Synchronous: waits for each workorder to complete before next (unless --parallel)
- Full tool support: read, write, shell, glob, search (all custom tools from workorder 02)
- Conflict validation: must not allow both custom + built-in tools (Gemini API constraint)
- Depends on workorder 02 (ToolExecutor), workorder 06 (built-in tools), workorder 07 (cache)
- All paths relative to `/c/csc/`
