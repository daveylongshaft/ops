---
urgency: P2
agent: haiku
requires: python,google-genai
tags: batch-api,converter
blockedBy: gemini-api-workflows-00-skeleton.md
---

# Workorder: Gemini Batch API - JSONL Converter

## Context
Create the converter that transforms CSC workorder .md files into Google Batch API JSONL format and back. This is the core interchange format between CSC and Google's batching system.

**Related:** Part 2 of 12-part series. Blocked by workorder 00.

## Deliverables

### Create `bin/gemini-batch/gbatch_convert.py`

**CLI Usage:**
```
gbatch_convert.py to-jsonl <workorder.md> [--model gemini-2.5-flash] [--out requests.jsonl]
gbatch_convert.py to-jsonl <batch_config.json> [--out requests.jsonl]
gbatch_convert.py from-results <results.jsonl> [--out summary.md]
gbatch_convert.py batch to-jsonl <workorders_dir/> [--out batch.jsonl]
```

### 1. `to-jsonl` Mode (Single Workorder → JSONL)
**Input:** `.md` workorder file
**Process:**
1. Parse YAML frontmatter (extract: `urgency`, `agent`, `model`, `requires` fields)
2. Strip frontmatter from content
3. Determine model: use `--model` override if provided, else from frontmatter, else default `gemini-2.5-flash`
4. Load system context via `common.load_system_context([CLAUDE.md, GEMINI.md, tools/INDEX.txt, tree.txt])`
5. Generate unique entry ID via `common.make_entry_id(filename)`
6. Build Gemini JSONL object:
   ```json
   {
     "key": "<entry_id>",
     "request": {
       "model": "models/gemini-2.5-flash",
       "system_instruction": "<system_context>",
       "contents": [
         {
           "role": "user",
           "parts": [
             {"text": "<workorder_content>"}
           ]
         }
       ],
       "generation_config": {
         "max_output_tokens": 8192,
         "temperature": 0
       }
     }
   }
   ```
7. Write JSONL line to stdout or `--out` file

**Note:** System instruction = full context for the model to understand CSC architecture

### 2. `to-jsonl` Mode (Batch Config → JSONL)
**Input:** `batch_config.json`
**Process:**
1. Load config via `common.load_config(path)`
2. Filter entries with `"provider": "gemini"` (ignore Claude entries)
3. For each Gemini entry:
   - Read workorder file path
   - Call `to-jsonl` logic on that file with model from config
   - Append to output JSONL
4. Write combined JSONL to stdout or `--out` file

### 3. `from-results` Mode (Results JSONL → Markdown Summary)
**Input:** Results JSONL from Google Batch API
**Process:**
1. For each line in results.jsonl:
   ```json
   {
     "key": "<entry_id>",
     "response": {
       "candidates": [
         {
           "content": {
             "parts": [
               {"text": "response text..."}
             ]
           }
         }
       ]
     }
   }
   ```
2. Extract: `response.candidates[0].content.parts[*].text` (concatenate if multiple parts)
3. Build markdown summary:
   ```markdown
   ## Result: <entry_id>

   <response_text>
   ```
4. Write to stdout or `--out` file

### 4. `batch to-jsonl` Mode (Directory → JSONL)
**Input:** Directory of workorders (e.g., `workorders/gemini-api/`)
**Process:**
1. Glob `*.md` files from directory
2. For each: call `to-jsonl` logic
3. Combine into single JSONL (one line per entry)
4. Write to `--out` (default: `batch.jsonl`)

### Error Handling
- Missing CLAUDE.md or GEMINI.md: log warning, continue with partial context
- Invalid YAML frontmatter: raise clear error with line number
- Invalid model name: suggest valid models, use default
- File not found: raise FileNotFoundError with readable path

## Testing Notes
- Parse sample workorder frontmatter with and without `model` field
- Verify JSONL structure matches Google Batch API schema
- Verify `from-results` reconstructs valid markdown
- Verify `batch to-jsonl` produces combined JSONL with all entries

## Notes
- Does NOT interact with Google API (pure serialization)
- Depends on workorder 00 for `common.py` utilities
- All paths relative to `/c/csc/`
