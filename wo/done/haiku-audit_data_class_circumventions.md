---
urgency: P2
description: Audit codebase for Data class circumventions and create fix workorders
---

# Audit: Data Class Circumvention Detection

## Task
Audit the entire CSC codebase to find places where the Data class is being circumvented (raw file I/O, direct JSON writes, etc.) instead of using the persistent Data framework.

This audit will CREATE a series of fix workorders (`data_storage-00.md` through `data_storage-NN.md`) that can then be run in batch with haiku (cheapest) using queue-worker (persistent).

## Background

The project has a proper data persistence architecture:
```
Root → Log → Data → Version → Platform → Network → Service
```

**Data Class Benefits:**
- Persistent storage with thread-safe locks
- Platform-aware directory management (uses temp/csc/run/, NOT project root)
- Single source of truth for runtime state
- Automatic persistence across restarts
- Unified key-value API

**Problem:** Code throughout the codebase bypasses this framework with raw file I/O.

## Search Patterns (grep for circumventions)

Search for these patterns in `/c/csc/packages/`:

1. **Raw .json file writes** (should use put_data instead)
   ```
   grep -r "\.write_text.*json\|json\.dump\|open.*'w'" --include="*.py"
   ```

2. **Raw .json file reads** (should use get_data instead)
   ```
   grep -r "\.read_text\|json\.load\|open.*'r'" --include="*.py"
   ```

3. **Project root file creation** (WRONG - should use temp/csc/run/)
   ```
   grep -r "self\.csc_root\s*/\|csc_root\s*/" --include="*.py"
   ```

4. **Path(".../file").write_text** (should use Data.put_data)
   ```
   grep -r "Path.*write_text\|Path.*write_bytes" --include="*.py"
   ```

5. **Hard-coded file paths** (should use Data.source_filename)
   ```
   grep -r "\.json\"\s*$\|\.txt\"\s*$\|\.log\"\s*$" --include="*.py" | grep -v test
   ```

## Expected Violations (with examples)

**Look for code like:**
```python
# WRONG - Raw file I/O
pid_file = self.csc_root / "service.pid"
pid_file.write_text(str(os.getpid()))
pid = int(pid_file.read_text())

# WRONG - Direct JSON
with open("runtime_state.json", "w") as f:
    json.dump(state, f)

# WRONG - Project root storage
config_path = csc_root / "config.json"
```

**Should be:**
```python
# CORRECT - Using Data class
self.put_data("service_pid", os.getpid())
pid = self.get_data("service_pid")

# CORRECT - Inheriting from Data
class MyService(Data):
    def __init__(self):
        super().__init__()
        self.source_filename = "myservice_state.json"
```

## Your Tasks

1. **Run all 5 grep patterns** from the search list above
2. **Document findings** in a summary:
   - File path
   - Line number
   - Current pattern (what's wrong)
   - Suggested fix (use Data class)

3. **For each violation found**, create a workorder in `workorders/ready/`:
   - **Filename format**: `data_storage-00.md`, `data_storage-01.md`, `data_storage-02.md`, etc.
   - Include file path, line number, current code, and how to fix it
   - Use urgency P3 (batch job - cost optimization)
   - Mark `cost_sensitive: true` to keep costs lowest
   - Mark `requires: bash, git` so it can run tests
   - This allows them to run as a batch with haiku + queue-worker (cheapest)

## Example Workorder Format

For each violation, create with **numbered filename** `data_storage-NN.md`:
```
---
urgency: P3
description: Fix data storage circumvention in <component>
cost_sensitive: true
requires: bash, git
---

## Violation Location
- File: packages/csc-service/csc_service/infra/xyz.py:45
- Pattern: Direct JSON file write

## Current Code
[code snippet]

## Should Be
[corrected code using Data class]

## Implementation Steps
1. Read the file and understand the current approach
2. Determine what data is being stored (e.g., PID, config, state)
3. Create or extend a Data subclass to manage this data
4. Replace raw file I/O with put_data/get_data calls
5. Test that the change works (manually verify behavior)
6. Commit with message: "fix: Convert [component] to use Data class"

## Why This Matters
- Keeps runtime files in temp/csc/run/ (not project root)
- Thread-safe persistence
- Single source of truth
- Platform-aware directory management
```

## Completion Criteria

✅ All 5 grep patterns run and results documented
✅ Violations summarized (file, line, pattern, fix)
✅ Workorders created for each violation in `data_storage-00.md` through `data_storage-NN.md`
✅ All workorders in `workorders/ready/` with P3 + cost_sensitive flags
✅ Audit workorder moved to `workorders/done/` when complete

## Batch Execution Plan

After you complete this audit:
1. All `data_storage-XX.md` workorders will be in `workorders/ready/`
2. They will be assigned to haiku using queue-worker (P3 + cost_sensitive)
3. Batch execution: haiku will run them with:
   - **Queue-worker** (persistent, resumable)
   - **Prompt caching** (90% cost savings)
   - **Haiku model** (cheapest)
   - Total cost for all conversions: **estimated $0.10-0.50** (vs $5+ with direct API)

## Notes

- Focus on high-value violations (services, PM, queue-worker, test-runner first)
- Ignore test files (tests/ directory)
- Ignore generated files (tools/, analysis_report.json, etc.)
- Prioritize violations in:
  - packages/csc-service/csc_service/infra/ (highest)
  - packages/csc-service/csc_service/shared/ (high)
  - packages/csc-service/csc_service/cli/ (medium)

## References

- Data class: packages/csc-service/csc_service/shared/data.py
- Log class: packages/csc-service/csc_service/shared/log.py
- Platform inheritance: packages/csc-service/csc_service/shared/platform.py
- Updated example: packages/csc-service/csc_service/infra/pm_executor.py (uses Data class correctly now)

---

When complete, move this workorder to `workorders/done/` and list the workorder count (data_storage-00 through data_storage-NN).


--- Agent Log ---
Perfect! I have successfully completed the data class circumvention audit. Here's what was accomplished:

## 🎯 Audit Completion Summary

### ✅ Work Completed

**1. Five Search Patterns Executed:**
- Pattern 1: Raw .json file writes (json.dump with open, Path.write_text)
- Pattern 2: Raw .json file reads (json.load with open, Path.read_text)
- Pattern 3: Project root file creation (csc_root / paths)
- Pattern 4: Path write operations (Path().write_text/write_bytes)
- Pattern 5: Hard-coded file paths (.json, .txt, .log files)

**2. Violations Found:**
- ~25 direct JSON write instances
- ~20 direct JSON read instances
- 7 project root path references
- 20+ hard-coded file paths
- **15 components across 25+ files affected**

**3. Workorders Created: 16 Total**
- `data_storage-00.md` - PM state persistence
- `data_storage-01.md` - Queue worker state
- `data_storage-02.md` - PM executor settings
- `data_storage-03.md` - Persistent clients
- `data_storage-04.md` - Server storage
- `data_storage-05.md` - Server data module
- `data_storage-06.md` - API key manager
- `data_storage-07.md` - Server version module
- `data_storage-08.md` - Config manager
- `data_storage-09.md` - PM main config
- `data_storage-10.md` - AI client state (Claude, Gemini, ChatGPT, DMRBot)
- `data_storage-11.md` - IRC bridge
- `data_storage-12.md` - Docker client
- `data_storage-13.md` - PM agent catalog
- `data_storage-14.md` - Scriptbot
- `data_storage-15.md` - CSC service client

**4. Audit Summary Created:**
- `AUDIT_SUMMARY-data_class_circumventions.md` - Comprehensive findings documentation

**5. Journal Entries:**
- All steps properly journaled via `python bin/next_step`
- Marked as COMPLETE per requirements

### 🚀 Next Steps

All 16 workorders are now in `workorders/ready/` with:
- **Urgency**: P3 (low priority batch job)
- **cost_sensitive**: true (optimizes for cost)
- **requires**: bash, git (enables testing)

**Queue Worker will:**
1. Pick up all P3 workorders
2. Assign to haiku (cheapest model)
3. Use prompt caching (90% cost savings)
4. Execute in parallel batches
5. **Total estimated cost: $0.10-0.50** (vs $5+ with direct API)

### 📊 Violations by Severity

| Priority | Count | Components |
|----------|-------|------------|
| High (Critical Infra) | 3 | PM, Queue Worker, PM Executor |
| High (Server Core) | 3 | Persistent Clients, Storage, Data Module |
| Medium | 4 | Config, API Keys, Version, Bridge |
| Standard | 6 | AI Clients, Docker, Scriptbot, CSC Client |

All violations focus on converting raw file I/O to use the Data class framework for atomic, thread-safe, platform-aware persistence.
[run_agent] Agent: haiku, Root: C:\Users\davey\AppData\Local\Temp\csc\haiku\repo, WIP: haiku-audit_data_class_circumventions.md
[run_agent] Git pull to get work files...
[run_agent] Git pull complete
[run_agent] ERROR: ANTHROPIC_API_KEY not set
[run_agent] Falling back to Claude CLI...
[run_agent] Starting Claude CLI (claude-haiku-4-5-20251001) for haiku
[run_agent] System prompt: 1038 chars (cacheable)
[run_agent] User prompt: 590 chars


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.
