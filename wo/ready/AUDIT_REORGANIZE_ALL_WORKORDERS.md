---
urgency: P1
tags: infrastructure,audit,reorganization,system-wide
requires: [python3, git, bash, find]
---

# Audit & Reorganize: All 567 Workorders for New System Structure

## Objective

Comprehensive audit of entire workorder system. Scan all 567 workorders in `/c/csc/ops/wo/` across all subdirectories, determine which still apply to the new system (restructured csc with Jules integration, CSCS encryption, new folder layout), update applicable ones, archive dead ends, and generate complete audit report.

## Context: New System Structure

**Major Changes**:
- Folder structure: `/c/csc/irc/` (code), `/c/csc/ops/` (AI instructions/workorders)
- Workorders: `workorders/` → `ops/wo/` (subdirs: ready, wip, done, hold, archive, run_next, batch)
- Agents: `agents/` → `ops/agents/` (queue-based assignment)
- Protocol rename: "IRC" → "CSC" (UDP), "CSCS" (encrypted)
- Path resolution: All paths via `Platform()` (no hardcoding)
- One class per file standard enforced

**What Workorders Need Updating**:
1. References to `workorders/` path → update to `ops/wo/`
2. References to `agents/` path → update to `ops/agents/`
3. Agent assignment format (old: `agent assign filename.md`) → still works, no change needed
4. Protocol references: "IRC" → "CSC" for UDP, "CSCS" for encrypted
5. Path references: hardcoded paths → use `Platform().get_abs_root_path()`
6. Old infrastructure paths (csc_service/clients/*, bin/claude-batch/, etc.)

**What Workorders Are Dead Ends** (mark "dead end" + archive):
1. Already completed before restructure (check if in done/ and was from pre-March 2026)
2. Superseded by new architecture (e.g., old queue system docs that are now handled by ops/agents/)
3. Deprecated infrastructure (old batch systems that were replaced)
4. Broken references to deleted repos (syscmdr, syscmdr-II, systemcommander) - archive with note
5. Workorders about file paths that no longer exist
6. Workorders for agents that no longer exist (old agent directories)

**What Workorders Still Apply** (leave in place):
1. Active development in ready/, wip/, run_next/
2. Current infrastructure features (pm.py, queue_worker, agent_service, etc.)
3. Recent features (CSCS encryption, Jules integration, plan-review agent - these are NEW, just assigned)
4. Bug fixes for current system
5. Documentation about current architecture
6. Workorders with current agent assignment (haiku, sonnet, opus, gemini, etc.)

## Execution Steps

### Step 1: Create Directory Structure

```bash
mkdir -p /c/csc/ops/wo/need_update/ready
mkdir -p /c/csc/ops/wo/need_update/wip
mkdir -p /c/csc/ops/wo/need_update/run_next
```

### Step 2: Scan All Workorders

For each `.md` file in `/c/csc/ops/wo/` (across all subdirs):

1. Read file to determine:
   - **File path**: `/c/csc/ops/wo/[subdir]/[filename]`
   - **Subdir**: ready, wip, done, hold, archive, batch, gemini-api, run_next
   - **Brief description**: First sentence or first ~100 chars of content (after YAML frontmatter)
   - **Current status**: Which subdirectory it's in

2. Analyze content for update needs:
   - Search for: `workorders/`, `agents/`, hardcoded paths like `/c/csc/` or `C:\csc\`
   - Search for: old agent names (no longer used)
   - Search for: "IRC" (should be "CSC" or "CSCS")
   - Search for: references to deleted repos (syscmdr, syscmdr-II, systemcommander, client-server-commander)
   - Search for: references to old /agents/ or /bin/claude-batch/ or other pre-restructure paths

3. Decision logic:

```
IF (marked "dead end" already OR completed before March 2026 OR references deleted repos):
    ACTION: Mark "dead end" on last line (format: "---\ndeadend: true\n---\n" or add comment)
    MOVE TO: /c/csc/ops/wo/archive/

ELIF (contains path references like "workorders/" OR "agents/" OR hardcoded paths):
    ACTION: Needs update - paths must be changed
    MOVE TO: /c/csc/ops/wo/need_update/[current_subdir]/
    NOTES: Document what needs updating

ELIF (contains "IRC" when should be "CSC"/"CSCS"):
    ACTION: Needs update - protocol terminology
    MOVE TO: /c/csc/ops/wo/need_update/[current_subdir]/
    NOTES: Document protocol renames needed

ELIF (references agents/ or old agent structure):
    ACTION: Needs update or verify it's still valid
    CHECK: If still applies → leave in place, if dead end → archive

ELSE (no issues found, still applies to current system):
    ACTION: Leave in place
    NO MOVE
```

### Step 3: Generate Audit Report

Create comprehensive markdown audit report at:
**File**: `/c/csc/ops/wo/results/WORKORDER_AUDIT_REPORT_[TIMESTAMP].md`

**Report Format**:

```markdown
# Workorder System Audit Report

Generated: [TIMESTAMP]
Total Scanned: 567
Total Reorganized: [N]

## Summary Statistics

- Still Apply (No Changes): [N]
- Need Updates: [N] (moved to need_update/)
- Dead Ends: [N] (moved to archive/)
- Already in Correct Location: [N]

## Reorganization Actions

### Moved to need_update/ready/ ([N] workorders)
| Filename | Issue | Action Required |
|----------|-------|-----------------|
| file1.md | Contains "workorders/" path | Update path references to ops/wo/ |
| file2.md | References old agents/ | Update agent paths to ops/agents/ |

### Moved to need_update/wip/ ([N] workorders)
| Filename | Issue | Action Required |
|----------|-------|-----------------|
| ... | ... | ... |

### Moved to need_update/run_next/ ([N] workorders)
| Filename | Issue | Action Required |
|----------|-------|-----------------|
| ... | ... | ... |

### Archived as Dead Ends ([N] workorders)
| Filename | Reason | Notes |
|----------|--------|-------|
| completed-work.md | Already completed | Completed before system restructure |
| old-repo-ref.md | References deleted repo | syscmdr removed in restructure |

### Still Apply (No Changes) ([N] workorders)
| Filename | Current Location | Status |
|----------|-----------------|--------|
| CSCS_ENCRYPTION.md | ready/ | Active |
| JULIUS_INTEGRATION.md | ready/ | Active |

## Detailed Workorder List (All 567)

### Ready Queue ([N] workorders)
- filename.md: brief description | Status: [apply/update/dead] | Action: [moved/left]
- ...

### WIP Queue ([N] workorders)
- filename.md: brief description | Status: [apply/update/dead] | Action: [moved/left]
- ...

### Run Next Queue ([N] workorders)
- filename.md: brief description | Status: [apply/update/dead] | Action: [moved/left]
- ...

### Done Archive ([N] workorders)
- filename.md: brief description | Status: [apply/update/dead] | Action: [left/archived]
- ...

### Hold Queue ([N] workorders)
- filename.md: brief description | Status: [apply/update/dead] | Action: [left/moved]
- ...

### Batch Queue ([N] workorders)
- filename.md: brief description | Status: [apply/update/dead] | Action: [left/moved]
- ...

### Archive ([N] workorders)
- filename.md: brief description | Status: [apply/update/dead] | Action: [left/archived]
- ...

## Key Findings

### Pattern 1: Path References Needing Updates
Example references found:
- `workorders/` appearing in [N] files
- `agents/` appearing in [N] files
- Hardcoded `/c/csc/` appearing in [N] files

### Pattern 2: Protocol Terminology
- "IRC" references: [N] files (should be "CSC" or "CSCS")
- Correct "CSC/CSCS" usage: [N] files

### Pattern 3: Dead Workorders
- Completed before restructure: [N] files
- References to deleted repos: [N] files
- Orphaned task references: [N] files

## Next Steps

1. **Review need_update/ workorders** - Agent assigned to fix path/terminology issues
2. **Archive review** - Manual spot-check that dead ends are truly no longer needed
3. **Integration** - Once fixed, move need_update/ workorders back to ready/wip/run_next/
4. **Cleanup** - Remove dead ends from git tracking (git rm)

---

**Report generated by workorder audit system**
**All workorders accounted for and reorganized**
**System ready for next phase of work**
```

## Code Standards (Critical)

- ✅ Use `pathlib.Path` for all file operations
- ✅ Use `Platform()` for path resolution (never hardcode paths)
- ✅ Log every action: "Scanned X files", "Moved Y to need_update/", "Archived Z as dead ends"
- ✅ Error handling: If file unreadable, log and skip (don't crash)
- ✅ Preserve file content exactly when moving (use Path.rename())
- ✅ Python 3.8+, type hints for functions
- ✅ Docstrings for all functions

## Success Criteria

✅ All 567 workorders scanned (verified by count)
✅ Workorders correctly categorized (apply/update/dead)
✅ need_update/ structure created with subdirs (ready, wip, run_next)
✅ Workorders moved to correct locations (no files left in wrong place)
✅ Dead ends marked with "dead end" comment/tag and archived
✅ Comprehensive audit report generated with statistics and details
✅ Report saved to ops/wo/results/ with timestamp
✅ Git status clean: only moved files, no deletions or modifications
✅ All 567 workorders still exist (just reorganized)

## Notes

- This is a meta-workorder: auditing the workorder system itself
- High volume: 567 files to process
- Critical: Don't delete any files, only move/reorganize
- Report first: Generate audit report BEFORE moving files
- Verify counts: Ensure every workorder is accounted for in final report

## Assumption

The system has reorganized to:
- `/c/csc/irc/` = CODE (Python packages, executables)
- `/c/csc/ops/` = AI INSTRUCTIONS (workorders, agent queue dirs, templates)
- All workorders now live in `/c/csc/ops/wo/` with subdir structure

This audit confirms the system is correctly organized post-restructure.

---

**Use your best judgment on:**
- Heuristics for detecting "dead end" vs "still applies"
- When to mark "needs update" vs "leave in place"
- Level of detail in audit report (CSV vs detailed list)
- Performance: handling 567 files efficiently (batch reads, minimal I/O)
- What counts as a "reference" that needs updating (exact string match vs semantic)

**CRITICAL**: If uncertain whether a workorder applies, mark as "needs_human_review" rather than deleting. Better to keep and review than lose valuable context.

READY FOR IMPLEMENTATION
