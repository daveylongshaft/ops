---
urgency: P2
agent: haiku
requires: python,pytest,mocking
tags: testing,unit-tests,no-api-calls
blockedBy: gemini-api-workflows-00-skeleton.md,gemini-api-workflows-02-tools.md,gemini-api-workflows-05-config.md,gemini-api-workflows-06-builtin.md
---

# Workorder: Gemini Batch API - Unit Tests

## Context
Create comprehensive unit test suite for the Gemini batch pipeline. All tests use mocking (no live API calls) and cover core functionality of each module.

**Related:** Part 10 of 12-part series. Blocked by workorders 00, 02, 05, 06. Required before final integration.

## Deliverables

### Create `tests/test_gemini_batch.py`

Test file structure (mirroring existing test patterns in codebase):
```python
import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import os

# Import modules under test
from bin.gemini_batch import common, converter, tools, config
```

### 1. Common Utilities Tests (`test_common.py` section)

**`test_load_config_creates_default()`**
- Mock filesystem
- Call `common.load_config()` on missing file
- Verify returns empty dict or default structure
- Verify no FileNotFoundError raised

**`test_save_config_atomic_write()`**
- Mock `open` and file ops
- Call `common.save_config(path, config_dict)`
- Verify writes to temp file first
- Verify atomic rename attempt

**`test_make_entry_id_deterministic()`**
- Call `make_entry_id("test.md")` twice
- Verify same filename produces same ID
- Verify ID format: `<timestamp>-<hash>`
- Verify hash includes filename

**`test_load_system_context_concatenates_files()`**
- Create temp files: CLAUDE.md, GEMINI.md, tree.txt, tools/INDEX.txt
- Call `load_system_context([...])`
- Verify all content present in result
- Verify section headers added between files

**`test_format_workorder_strips_frontmatter()`**
- Create workorder with YAML frontmatter
- Call `format_workorder(path)`
- Verify YAML removed
- Verify content body returned

**`test_gemini_models_constant_has_valid_names()`**
- Verify `GEMINI_MODELS` dict has at least: `gemini`, `gemini-3-pro`, `gemini-2`
- Verify all values start with `"models/"`

---

### 2. Converter Tests

**`test_convert_workorder_to_jsonl_single()`**
- Create sample workorder.md with YAML frontmatter
- Call `converter.to_jsonl(path)`
- Verify output is valid JSON (one line)
- Verify structure:
  ```json
  {
    "key": "<entry_id>",
    "request": {
      "model": "models/gemini-2.5-flash",
      "system_instruction": "<content>",
      "contents": [{"role": "user", "parts": [...]}],
      "generation_config": {}
    }
  }
  ```

**`test_convert_workorder_model_override()`**
- Create workorder with model in frontmatter
- Call with `--model` CLI override
- Verify CLI override wins

**`test_convert_results_to_markdown()`**
- Create sample results JSONL (Google Batch API format)
- Call `converter.from_results(path)`
- Verify markdown output
- Verify each result becomes a section
- Verify response text extracted correctly

**`test_convert_batch_config_filters_provider()`**
- Create batch_config.json with mixed claude + gemini entries
- Call `converter.batch_to_jsonl(config_path)`
- Verify only gemini entries in output
- Verify claude entries ignored

**`test_convert_invalid_yaml_frontmatter()`**
- Create workorder with malformed YAML
- Call converter
- Verify clear error with line number

---

### 3. Tools Tests

**`test_tool_executor_read_file()`**
- Mock filesystem with temp file
- Create `ToolExecutor`, call `execute(read_file_call)`
- Verify correct content returned
- Verify handles missing files gracefully

**`test_tool_executor_write_file()`**
- Mock filesystem
- Create `ToolExecutor`, call `execute(write_file_call)`
- Verify file created with correct content
- Verify parent directories created

**`test_tool_executor_run_command_safe()`**
- Create `ToolExecutor`
- Test allowed commands: `echo`, `git status`, `python -c "print(1)"`
- Verify all execute successfully (mock subprocess)

**`test_tool_executor_run_command_blocked_rm()`**
- Create `ToolExecutor`, call with `rm -rf /path`
- Verify returned: `"BLOCKED: rm -rf pattern not allowed"`

**`test_tool_executor_run_command_blocked_force_push()`**
- Create `ToolExecutor`, call with `git push --force`
- Verify returned: `"BLOCKED: git push --force not allowed"`

**`test_tool_executor_get_declarations()`**
- Create `ToolExecutor`
- Call `get_tool_declarations()`
- Verify returns list of FunctionDeclaration objects
- Verify at least 6 tools (read, write, list, run, glob, search)

**`test_tool_loop_termination_on_no_function_calls()`**
- Mock Gemini client that returns text-only response (no function calls)
- Create `ToolExecutor`
- Call `run_tool_loop(...)`
- Verify loop terminates after one round
- Verify final answer extracted and returned

**`test_tool_loop_terminates_on_max_rounds()`**
- Mock Gemini client that always returns function calls (no final answer)
- Create `ToolExecutor`
- Call `run_tool_loop(..., max_rounds=3)`
- Verify exits after 3 rounds
- Verify returns error message about max rounds

**`test_tool_loop_executes_function_calls()`**
- Mock client: first response has function call, second has text answer
- Create `ToolExecutor`
- Call `run_tool_loop(...)`
- Verify function call executed
- Verify result fed back to API
- Verify loop continues and completes

---

### 4. Config Tests

**`test_gbatch_add_creates_entry()`**
- Mock `common.load_config`, `common.save_config`
- Call `config.add_entry(...)`
- Verify entry added with correct fields

**`test_gbatch_list_filters_provider()`**
- Load config with mixed providers
- Call `config.list_entries(provider="gemini")`
- Verify only gemini entries returned

**`test_gbatch_edit_updates_model()`**
- Load config, get entry
- Call `config.edit_entry(id, model="gemini-2.5-pro")`
- Verify model updated
- Verify other fields unchanged

**`test_gbatch_remove_deletes_entry()`**
- Load config with entries
- Call `config.remove_entry(id)`
- Verify entry removed from list
- Verify count decremented

---

### 5. Built-in Tools Tests

**`test_google_search_tool_get_tool()`**
- Create `GoogleSearchTool`
- Call `get_tool()`
- Verify returns Tool with google_search configured
- Verify tool type correct

**`test_google_search_extract_sources()`**
- Create mock response with grounding chunks:
  ```python
  response.candidates[0].content.parts[0].grounding_chunks = [
    {"title": "Foo", "uri": "http://foo.com", "snippet": "..."}
  ]
  ```
- Call `extract_sources(response)`
- Verify returns list with correct dicts

**`test_code_execution_tool_get_tool()`**
- Create `CodeExecutionTool`
- Call `get_tool()`
- Verify returns Tool with code_execution configured

**`test_code_execution_extract_results()`**
- Create mock response with code execution results
- Call `extract_results(response)`
- Verify returns list of dicts with code, output, outcome

**`test_builtin_tool_registry_get_tool()`**
- Create `BuiltinToolRegistry`
- Call `get_tool("google_search")`
- Verify returns GoogleSearchTool.get_tool()
- Call `get_tool("code_execution")`
- Verify returns CodeExecutionTool.get_tool()

**`test_builtin_tool_registry_parse_names()`**
- Create `BuiltinToolRegistry`
- Call `parse_names("code_execution,google_search")`
- Verify returns `["code_execution", "google_search"]`
- Test with spaces, empty strings, etc.

**`test_builtin_tool_validate_no_conflict_error()`**
- Create `BuiltinToolRegistry`
- Call `validate_no_conflict(custom_tool_count=1)`
- Verify raises ValueError
- Verify error message mentions Gemini 3.x limitation

---

### 6. Batch Runner Tests

**`test_batch_submit_uploads_and_creates()`**
- Mock file upload, batch creation
- Call `gbatch_run.submit(...)`
- Verify file uploaded
- Verify batch created with correct model
- Verify metadata saved

**`test_batch_polling_complete()`**
- Mock batch status as COMPLETED
- Call `gbatch_run.status(...)`
- Verify message includes completion info

**`test_batch_polling_timeout()`**
- Mock batch status as QUEUED for many rounds
- Call `gbatch_run.run(...)` with 1 second timeout
- Verify gracefully exits and saves job name

**`test_batch_retrieve_downloads_results()`**
- Mock completed batch with results
- Call `gbatch_run.retrieve(...)`
- Verify results JSONL written
- Verify cost calculated

---

### 7. Tool-Loop Runner Tests

**`test_tool_run_single_workorder()`**
- Create sample workorder
- Mock `ToolExecutor.run_tool_loop()`
- Call `gbatch_tool_run.run_workorder(...)`
- Verify result returned
- Verify tokens counted

**`test_tool_run_builtin_conflict()`**
- Create workorder with `--builtin code_execution` and `--builtin google_search`
- Call `gbatch_tool_run.run_workorder(...)`
- Verify error about conflict

**`test_tool_run_batch_parallel()`**
- Create 3 mock workorders
- Call `gbatch_tool_run.run_batch(..., parallel=2)`
- Verify ThreadPoolExecutor used with 2 workers
- Verify all 3 complete

**`test_tool_run_cache_hit()`**
- Mock `CacheManager.get_active()` returning cache name
- Call `gbatch_tool_run.run_workorder(..., cache=True)`
- Verify cache name embedded in request

---

### 8. Queue Integration Tests

**`test_queue_mode_selection()`**
- Create workorder with `requires: [file_io]`
- Call `gbatch_queue_run.infer_mode(...)`
- Verify returns "tool-loop"
- Create workorder with `requires: []`
- Verify returns "batch-api"

**`test_queue_process_single_workorder_success()`**
- Mock workorder in wip/
- Mock tool runner success
- Call queue processor
- Verify workorder moved to done/

**`test_queue_git_sync_on_completion()`**
- Mock git commands
- Call queue processor with multiple workorders
- Verify `git add`, `git commit`, `git push` called at end

---

## Running Tests

```bash
# Run all Gemini batch tests
python -m pytest tests/test_gemini_batch.py -v

# Run specific test class
python -m pytest tests/test_gemini_batch.py::TestConverter -v

# Run with coverage
python -m pytest tests/test_gemini_batch.py --cov=bin.gemini_batch
```

## Notes
- All tests use `unittest.mock` (no live API calls)
- Fixtures for temp files, mock responses provided
- Tests follow existing CSC test conventions
- No Gemini API key needed to run tests
- Expected coverage: >90% of codebase
