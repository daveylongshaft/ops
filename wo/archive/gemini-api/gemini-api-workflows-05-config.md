---
urgency: P2
agent: haiku
requires: python
tags: config,cli,crud
blockedBy: gemini-api-workflows-00-skeleton.md
---

# Workorder: Gemini Batch API - Config Management Scripts

## Context
Create CLI tools for managing Gemini batch entries in `batch_config.json`. Four simple scripts mirror the Anthropic batch config tools.

**Related:** Part 6 of 12-part series. Blocked by workorder 00 (needs common.py). No blockers on other workorders.

## Deliverables

### Create `bin/gemini-batch/gbatch_add.py`

**Usage:**
```
gbatch_add.py <workorder.md> [--model gemini-2.5-flash] [--agent gemini]
              [--provider gemini] [--tools code_execution,google_search]
```

**Process:**
1. Read workorder file path
2. Verify file exists, is readable
3. Extract YAML frontmatter if present (model, builtin, etc.)
4. Get or create `batch_config.json` in `bin/gemini-batch/` via `common.load_config()`
5. Generate unique entry ID via `common.make_entry_id(workorder_basename)`
6. Create entry:
   ```json
   {
     "id": "<entry_id>",
     "workorder": "<path>",
     "model": "gemini-2.5-flash",
     "agent": "gemini",
     "provider": "gemini",
     "builtin_tools": ["code_execution"],  // optional, may be empty
     "added_at": "2026-03-03T12:34:56Z"
   }
   ```
7. Append to `batch_config.json` `entries` array
8. Save via `common.save_config()`
9. Print: `"Added entry <id> for <workorder>. Model: gemini-2.5-flash, tools: code_execution"`

**Validation:**
- Workorder file must exist
- Model must be in `GEMINI_MODELS` dict
- Provider must be "gemini"
- Tools must be from allowed list (code_execution, google_search)

---

### Create `bin/gemini-batch/gbatch_list.py`

**Usage:**
```
gbatch_list.py [--provider gemini] [--model gemini-2.5-flash] [--summary]
```

**Process:**
1. Load `batch_config.json` via `common.load_config()`
2. Filter by `--provider` (default: gemini) and `--model` if specified
3. For each entry:
   - Print: `[ID] <workorder> | Model: <model> | Tools: <tools>`
   - Include file status (exists/missing)
4. Print summary: `"<N> Gemini entries, <M> with tools, <P> missing files"`
5. If `--summary`: just print totals without details

---

### Create `bin/gemini-batch/gbatch_edit.py`

**Usage:**
```
gbatch_edit.py <entry_id_or_workorder> [--model gemini-2.5-pro]
               [--tools code_execution,google_search] [--agent gemini]
```

**Process:**
1. Load `batch_config.json`
2. Find entry by ID or workorder filename (search `entries` array)
3. If not found: print error, exit
4. Update fields: model, builtin_tools, agent (only specified fields)
5. Save via `common.save_config()`
6. Print: `"Updated entry <id>: model=gemini-2.5-pro, tools=code_execution,google_search"`

---

### Create `bin/gemini-batch/gbatch_remove.py`

**Usage:**
```
gbatch_remove.py <entry_id_or_workorder> [--force]
```

**Process:**
1. Load `batch_config.json`
2. Find entry by ID or workorder filename
3. If not found: print error, exit
4. If no `--force`: prompt user: `"Remove entry <id>? (yes/no)"`
5. Remove entry from `entries` array
6. Save via `common.save_config()`
7. Print: `"Removed entry <id>"`

---

## Testing Notes
- Unit test: `test_gbatch_add_creates_entry()` — verify entry added to config
- Unit test: `test_gbatch_list_filters_provider()` — verify only gemini entries shown
- Unit test: `test_gbatch_edit_updates_model()` — verify model updated
- Unit test: `test_gbatch_remove_deletes_entry()` — verify entry deleted
- Unit test: `test_gbatch_add_missing_file()` — verify error if workorder doesn't exist

## Notes
- All scripts use `common.load_config()` and `common.save_config()`
- Entry ID format matches `common.make_entry_id()` pattern (timestamp + hash)
- Provider is always "gemini" for this suite (Claude entries use provider="claude")
- Workorder path is relative to `/c/csc/`
