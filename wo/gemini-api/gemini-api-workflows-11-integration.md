---
urgency: P2
agent: haiku
requires: python,google-genai,pytest,git
tags: integration,smoke-test,final-verification
blockedBy: gemini-api-workflows-00-skeleton.md,gemini-api-workflows-09-tests.md,gemini-api-workflows-10-docs.md
---

# Workorder: Gemini Batch API - Integration & Smoke Test

## Context
Final integration step: verify all components wire together, dependencies are correct, and basic smoke tests pass. Create sample workorder and run end-to-end test without full API execution (can use live API if key available, but tests must pass without it).

**Related:** Part 12 of 12-part series (FINAL). Blocked by workorders 00, 09, 10.

## Deliverables

### 1. Verify Dependencies

**Check `pyproject.toml`:**
- Verify `google-genai` is in dependencies (or add if missing)
- Expected: `google-genai >= 0.4.0` (version that has client.batches, client.caches, etc.)
- Pin to a stable release if not already pinned

**If missing, add:**
```toml
[project]
dependencies = [
  ...existing...,
  "google-genai>=0.4.0",
]
```

---

### 2. Update `refresh-maps` Script

**Verify/Update `bin/refresh-maps` (or equivalent):**
- Add `bin/gemini-batch/` to the directories scanned for code maps
- Expected: generates `tools/gemini-batch.txt` (index of all functions/classes)
- Test: run `refresh-maps --quick` and verify `tools/gemini-batch.txt` created

```bash
# Existing pattern in refresh-maps:
for dir in packages/*/; do
  python bin/generate-code-map.py "$dir" > "tools/$(basename $dir).txt"
done

# Add:
python bin/generate-code-map.py bin/gemini-batch/ > tools/gemini-batch.txt
```

---

### 3. Create Sample Workorder

**Create `workorders/gemini-api/sample-test-workorder.md`:**
```markdown
---
urgency: P3
agent: haiku
model: gemini-2.5-flash
requires: []
tags: test,sample
---

# Sample Gemini Batch Test Workorder

List 3 files in `/c/csc/bin/gemini-batch/` directory (just the names, one per line).

This is a simple test workorder to verify the Gemini batch pipeline is working.
No complex processing needed — just list directory contents.
```

---

### 4. Run Converter Smoke Test

**Verify converter works without API:**
```bash
# Convert sample workorder to JSONL
python bin/gemini-batch/gbatch_convert.py to-jsonl workorders/gemini-api/sample-test-workorder.md --out /tmp/test.jsonl

# Verify output is valid JSON
python -c "import json; [json.loads(l) for l in open('/tmp/test.jsonl')]"
# Expected: no error, JSON is valid

# Verify structure
python -c "
import json
for line in open('/tmp/test.jsonl'):
    data = json.loads(line)
    assert 'key' in data, 'Missing key'
    assert 'request' in data, 'Missing request'
    assert 'model' in data['request'], 'Missing model'
    assert data['request']['model'] == 'models/gemini-2.5-flash'
    print(f'✓ Valid: {data[\"key\"]}')"
# Expected: ✓ Valid: entry-XXXXXX-XXXXXX
```

---

### 5. Run Unit Tests

**Run pytest with coverage:**
```bash
# All Gemini batch tests
python -m pytest tests/test_gemini_batch.py -v

# Expected output:
#  test_load_config_creates_default PASSED
#  test_save_config_atomic_write PASSED
#  test_make_entry_id_deterministic PASSED
#  ... (all tests pass)
#  ===================== XX passed in X.XXs =====================

# If any fail: stop and fix before proceeding
```

**Verify coverage:**
```bash
python -m pytest tests/test_gemini_batch.py --cov=bin.gemini_batch --cov-report=term-missing

# Expected: >90% coverage across all modules
```

---

### 6. Test Config Management

**Verify gbatch_add, gbatch_list, etc.:**
```bash
# Create a test config
rm -f bin/gemini-batch/batch_config.json

# Add entry
python bin/gemini-batch/gbatch_add.py workorders/gemini-api/sample-test-workorder.md \
  --model gemini-2.5-flash

# List entries
python bin/gemini-batch/gbatch_list.py
# Expected: shows 1 entry with workorder path, model, agent

# Edit entry
ENTRY_ID=$(python -c "import json; print(json.load(open('bin/gemini-batch/batch_config.json'))['entries'][0]['id'])")
python bin/gemini-batch/gbatch_edit.py $ENTRY_ID --model gemini-2.5-pro

# Verify edit
python bin/gemini-batch/gbatch_list.py | grep gemini-2.5-pro
# Expected: shows updated model

# Remove entry
python bin/gemini-batch/gbatch_remove.py $ENTRY_ID --force

# Verify empty
python bin/gemini-batch/gbatch_list.py
# Expected: 0 entries
```

---

### 7. Verify Imports & Syntax

**Check all Python files for syntax errors:**
```bash
# Compile all .py files
python -m py_compile bin/gemini-batch/*.py tests/test_gemini_batch.py
# Expected: no output (all files compile)

# Verify imports work
python -c "from bin.gemini_batch import common; print('✓ common imports OK')"
python -c "from bin.gemini_batch import gbatch_convert; print('✓ converter imports OK')"
python -c "from bin.gemini_batch import gbatch_tools; print('✓ tools imports OK')"
python -c "from bin.gemini_batch import gbatch_builtin; print('✓ builtin imports OK')"
# Expected: all ✓ messages
```

---

### 8. Verify Documentation

**Check docs exist and are readable:**
```bash
# Verify files exist
test -f docs/gemini-batch-api.md && echo "✓ docs/gemini-batch-api.md exists"
test -f GEMINI.md && echo "✓ GEMINI.md exists"

# Verify no broken markdown syntax (basic)
grep -E "^\[.*\]\(.*\)" docs/gemini-batch-api.md | head -3
# Expected: at least 3 links in markdown

# Verify code examples are present
grep -c "gbatch_" docs/gemini-batch-api.md
# Expected: >10 (multiple command examples)
```

---

### 9. Optional: Live API Smoke Test

**If GOOGLE_API_KEY is available (optional):**
```bash
# Set key
export GOOGLE_API_KEY="<your-key>"

# Run converter to JSONL
python bin/gemini-batch/gbatch_convert.py to-jsonl workorders/gemini-api/sample-test-workorder.md --out /tmp/test.jsonl

# (Optional) Submit real batch if API key available
# WARNING: This will cost money and create real batch jobs
# python bin/gemini-batch/gbatch_run.py run bin/gemini-batch/batch_config.json --async
# echo "Batch submitted. Check status via gbatch_run.py status <job_name>"
```

**If no API key: that's fine, converter smoke test above is sufficient**

---

### 10. Update Tools Index

**Regenerate code maps:**
```bash
# Run refresh-maps to include gemini-batch in catalog
bash bin/refresh-maps --quick

# Verify tools/gemini-batch.txt was created
test -f tools/gemini-batch.txt && echo "✓ Code map generated"

# Verify it lists classes/functions
grep -E "^def |^class " tools/gemini-batch.txt | head -5
# Expected: at least 5 function/class definitions listed
```

---

### 11. Git Commit

**Stage and commit all changes:**
```bash
# Check status
git status

# Expected to see:
#  new file:   bin/gemini-batch/__init__.py
#  new file:   bin/gemini-batch/common.py
#  new file:   bin/gemini-batch/gbatch_convert.py
#  ... (all new files)
#  new file:   docs/gemini-batch-api.md
#  modified:   GEMINI.md
#  modified:   tools/gemini-batch.txt
#  ... etc

# Stage everything
git add .

# Commit with message
git commit -m "feat: Implement Google Gemini API batch pipeline

- Common utilities (load_config, load_system_context, etc.)
- Converter: workorder .md ↔ Gemini JSONL formats
- Custom tool executor: read, write, list, run, glob, search
- Batch API runner: async submit/poll (50% discount)
- Tool-loop runner: sync with full tool execution
- Config CLI: add, list, edit, remove batch entries
- Built-in tools: google_search, code_execution wrappers
- Context caching: 90% input token savings
- Queue-worker integration: continuous automation
- Unit tests: >90% coverage, all mocked (no API calls)
- Documentation: user guide + CLI reference
- Sample workorder and smoke tests

Matches Anthropic batch pipeline architecture.
Mirrors existing codebase patterns.
All workorders (00-11) completed and integrated."

# Expected: commit succeeds
```

---

### 12. Create Verification Checklist

**Document verification in this workorder:**

Create a summary of all verification steps completed:

```
INTEGRATION VERIFICATION CHECKLIST
===================================

✓ Dependencies verified/updated (google-genai in pyproject.toml)
✓ refresh-maps updated to include bin/gemini-batch/
✓ Sample workorder created (sample-test-workorder.md)
✓ Converter smoke test passed (JSONL valid)
✓ All unit tests passed (pytest, >90% coverage)
✓ Config management scripts tested (add/list/edit/remove)
✓ All Python files syntax-checked (py_compile)
✓ All imports verified
✓ Documentation created (gemini-batch-api.md + GEMINI.md)
✓ Tools index generated (tools/gemini-batch.txt)
✓ Git commit created

SUMMARY:
- 12 workorders completed (00-11)
- 14 Python modules created (common, converter, tools, builtin, run, tool_run, add, list, edit, remove, cache, queue_run, __init__, tests)
- 2 documentation files (docs/gemini-batch-api.md, GEMINI.md update)
- 1 sample workorder (sample-test-workorder.md)
- All tests passing, no API calls required for base validation
- Ready for production use with GOOGLE_API_KEY env var

NEXT STEPS:
- Set GOOGLE_API_KEY env var to run live batches
- Try: gbatch_add.py <workorder> && gbatch_run.py run batch_config.json
- Monitor via: agent tail, gbatch_run.py status <job_name>
```

---

## Testing Strategy

**No Live API Calls Required:**
- Converter validated with JSONL schema
- Tools tested with mocks
- Config management tested with temp files
- All tests use unittest.mock

**Optional Live Test:**
- If GOOGLE_API_KEY available: can submit real batch (costs money)
- Otherwise: all smoke tests pass without API key

## Notes
- This workorder ties together all previous 11 workorders
- All files created by prior workorders should exist and import cleanly
- Smoke tests are quick (< 1 minute) and require no API calls
- After commit, Gemini batch pipeline is production-ready
- Next phase: users can assign Gemini workorders via `agent select gemini && agent assign <workorder>`
