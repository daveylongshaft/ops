---
urgency: P2
agent: haiku
requires: python,google-genai
tags: batch-api,infrastructure
---

# Workorder: Gemini Batch API - Skeleton & Common Utilities

## Context
Building a Google Gemini API batch pipeline mirroring the existing Anthropic batch pipeline in `bin/claude-batch/`. This workorder creates the foundational directory structure and shared utility functions.

**Related:** Part 1 of 12-part series (gemini-api-workflows-00 through -11)

## Deliverables

### 1. Create Directory Structure
```
bin/gemini-batch/
├── __init__.py
├── README.md
├── common.py
├── gbatch_convert.py       (workorder 01)
├── gbatch_tools.py         (workorder 02)
├── gbatch_run.py           (workorder 03)
├── gbatch_tool_run.py      (workorder 04)
├── gbatch_add.py           (workorder 05)
├── gbatch_list.py          (workorder 05)
├── gbatch_edit.py          (workorder 05)
├── gbatch_remove.py        (workorder 05)
├── gbatch_builtin.py       (workorder 06)
├── gbatch_cache.py         (workorder 07)
└── gbatch_queue_run.py     (workorder 08)
```

### 2. Create `bin/gemini-batch/__init__.py`
Empty file (standard Python package marker).

### 3. Create `bin/gemini-batch/README.md`
One-paragraph summary:
- Two modes: "batch-api" (async JSONL submit, 50% cheaper) and "tool-loop" (sync with tool execution)
- Built-in tools: `google_search`, `code_execution`
- Context caching: 90% input token savings
- Compatible with CSC workorder system

### 4. Create `bin/gemini-batch/common.py`
Core utilities for all other modules. Must include:

**Functions:**
- `load_config(path: str) -> dict` — reads `batch_config.json`, returns config dict
- `save_config(path: str, config: dict) -> None` — atomically writes `batch_config.json`
- `make_entry_id(filename: str) -> str` — generates timestamp-based unique ID matching `claude-batch/common.py` pattern
- `get_gemini_api_key() -> str` — imports from `packages/csc-service/csc_service/clients/gemini/secret.py:get_gemini_api_key()`
- `load_system_context(files: list[str]) -> str` — reads and concatenates: `CLAUDE.md`, `GEMINI.md`, `tools/INDEX.txt`, `tree.txt` with section headers
- `format_workorder(path: str) -> str` — reads .md file, strips YAML frontmatter, returns prompt string

**Constants:**
```python
GEMINI_MODELS = {
    "gemini": "models/gemini-2.5-flash",
    "gemini-3-pro": "models/gemini-2.5-pro",
    "gemini-2": "models/gemini-2.5-flash",
}
```
(Map from `bin/run_agent.py` lines 34-42, convert to full model names with `models/` prefix)

**Imports:**
- Standard: `json`, `os`, `sys`, `datetime`, `hashlib`
- Google: `google.genai` (import client via `google.genai.Client()`)

## Testing Notes
- No live API calls yet
- Verify functions exist and have correct signatures
- `make_entry_id()` must produce deterministic IDs for same filename

## Notes
- Does NOT create or modify batch_config.json (first entry added by workorder 05)
- All paths relative to `/c/csc/` root
- This workorder unblocks all others
