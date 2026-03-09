---
urgency: P0
tags: infrastructure,path,shell-tools,cross-platform,critical
requires: [python3, bash, git]
---

# Fix: System PATH & All Shell Tools (.bat, .sh, .py)

## Objective

Audit and fix **all 75+ shell tools** in `/c/csc/bin/`. Ensure every .bat, .sh, and .py script:
1. Uses correct Python interpreter (system `python`, not non-existent `venv`)
2. Resolves paths correctly (absolute, no hardcoding `/c/Users/davey/venv_manager`)
3. Works from any directory (tools in PATH)
4. Works in both Bash and PowerShell
5. Has proper shebang lines

Clean up and optimize system PATH.

## Problem

**Current State**:
- All .bat files hardcode: `"%~dp0..\venv\Scripts\python.exe"` → **doesn't exist**
- PATH is duplicated, messy, references dead venv
- Some .py files have no execution wrapper
- Some .sh files won't run on Windows (need .bat wrappers)
- agent.bat, refresh-maps.bat, trash.bat, csc-ctl.bat, etc. all broken

**Failed Tests**:
```
wo: OK (fixed)
agent: FAIL (venv ref)
refresh-maps: FAIL (venv ref)
trash: FAIL (venv ref)
csc-ctl: partial (needs fixes)
```

## Execution Plan

### Phase 1: Audit All Tools

Create comprehensive inventory:
- `/c/csc/bin/*.bat` — count, check shebang/first line, identify pattern
- `/c/csc/bin/*.sh` — count, check execution method
- `/c/csc/bin/*.py` — count, which have .bat wrappers, which are orphaned

**Output**: `tools_audit_report.txt` with:
```
=== BAT Files (53 total) ===
agent.bat              : References venv [BROKEN] → FIX: use python
refresh-maps.bat       : References venv [BROKEN] → FIX: use python
csc-ctl.bat            : Uses python [OK] but missing target script
...

=== SH Files (15 total) ===
pr-review-agent.sh     : Has shebang [OK]
setup-trash-aliases.sh : Has shebang [OK]
...

=== PY Files (35 total) ===
workorders_quick.py    : Standalone [OK]
batch_executor.py      : Needs wrapper? [?]
...

=== Missing/Orphaned ===
agent                  : .bat exists but calls non-existent agent script
csc-ctl                : .bat exists but calls non-existent csc-ctl script
...
```

### Phase 2: Fix BAT Files

**Template for all .bat files**:
```batch
@echo off
REM {description}
REM Auto-generated: uses system Python + proper argument passing
python "%~dp0{scriptname}" %*
```

**Fixes needed**:
1. Replace all `"%~dp0..\venv\Scripts\python.exe"` → `python`
2. Verify target script exists (if calling `python script`, script must be in bin/)
3. Check for broken references (e.g., agent.bat calls non-existent `agent` script)

**Broken chains to fix**:
- agent.bat → where is `agent` script? (doesn't exist in bin/)
- csc-ctl.bat → where is `csc-ctl` script? (doesn't exist in bin/)
- refresh-maps.bat → where is `refresh-maps` script? (doesn't exist in bin/)
- trash.bat → where is `trash` script? (doesn't exist in bin/)

**Resolution**: Either find/restore the scripts, or create wrapper Python scripts for missing ones.

### Phase 3: Create Missing Script Wrappers

For tools that don't have implementation:
- `agent` → Create as Python wrapper to `workorders_quick.py agent <args>`
- `refresh-maps` → Create as Python wrapper (for now: stub or point to existing implementation)
- `trash` → Create as Python wrapper for safe file deletion
- `csc-ctl` → Restore or recreate from csc-service package

**Minimum viable wrappers** (if originals missing):
```python
#!/usr/bin/env python3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def main():
    print(f"Tool not yet implemented: {Path(__file__).name}")
    print(f"Project root: {PROJECT_ROOT}")
    sys.exit(1)

if __name__ == "__main__":
    main()
```

Better: grep codebase for existing implementations and restore/link them.

### Phase 4: Fix PATH

**Current PATH issues**:
- Duplicated entries
- References non-existent `/c/csc/venv/Scripts`
- Includes `/cmd` (invalid)
- Includes multiple Windows paths duplicated

**Action**:
1. Extract unique PATH entries
2. Remove dead venv paths
3. Ensure `/c/csc/bin` is early (before system tools)
4. Remove duplicates
5. Generate clean PATH

**Set PATH** in shell profile (`.bashrc` or PowerShell profile):
```bash
# Clean system PATH - remove venv refs, dedupe
export PATH="/c/csc/bin:/c/Users/davey/bin:/c/Users/davey/.local/bin:$(echo $PATH | tr ':' '\n' | sort -u | grep -v venv | grep -v '/cmd' | paste -sd: -)"
```

### Phase 5: Verify All Tools

Test each tool after fixes:

```bash
# Core workorder tools
wo status
wo list ready
wo read 1

# Agent tools
agent --help  [if implemented]

# System tools
refresh-maps --help  [if implemented]
trash --help  [if implemented]
csc-ctl status  [if implemented]

# Other key tools
python /c/csc/bin/generate_tree.py
python /c/csc/bin/batch_executor.py --help
```

Expected: All return success (0 exit) or meaningful help message.

### Phase 6: Document & Verify

Create `bin/TOOLS_MANIFEST.md`:
```markdown
# CSC Tools Manifest

## Working Tools
- wo (workorders)
- refresh-maps
- trash
- ...

## Tools Needing Implementation
- agent (stub only)
- csc-ctl (partial)

## Tools Deprecated/Removed
- ...

## PATH Setup
Add to shell profile:
  export PATH="/c/csc/bin:..."
```

## Implementation Notes

### Key Decisions

1. **Python interpreter**: Always use system `python` (in PATH), never hardcode venv paths
2. **Script wrapper strategy**: For each tool, either:
   - **Direct .py script**: Call directly with python (e.g., `python wo_script.py`)
   - **.bat wrapper**: Call .py from .bat (for Windows native execution)
   - **Python wrapper**: If tool logic missing, create minimal wrapper that at least runs
3. **Missing scripts**: Search git history / packages/ for original implementations before creating stubs

### Testing Strategy

For each tool after fix:
```bash
# Test from bash
python /c/csc/bin/wo_script.py status

# Test from PowerShell (if .bat wrapper)
PS> wo status

# Test from anywhere in PATH
cd /tmp && wo status  # Should work from any dir
```

## Success Criteria

✅ All 75+ shell tools in `/c/csc/bin/` audited
✅ No venv references in any .bat file
✅ All .bat files use `python` (system interpreter)
✅ Missing scripts either restored or replaced with stubs
✅ PATH cleaned: no duplicates, no dead paths
✅ `/c/csc/bin` early in PATH (before system tools)
✅ All critical tools tested and working:
   - wo (workorders)
   - refresh-maps
   - trash
   - csc-ctl
   - agent (if applicable)
✅ Tools work from any directory
✅ Tools work in Bash and PowerShell
✅ `bin/TOOLS_MANIFEST.md` documents all tools + status

## Files to Create/Modify

**Audit & Fix**:
- All `/c/csc/bin/*.bat` (venv → python)
- All `/c/csc/bin/*.sh` (verify shebang)
- All `/c/csc/bin/*.py` (check if callable)

**Create**:
- `bin/TOOLS_MANIFEST.md` — inventory + status
- Missing script wrappers (agent, refresh-maps, trash, csc-ctl if missing)
- Clean PATH export script

**Modify**:
- User shell profiles (`.bashrc`, PowerShell `$PROFILE`) with clean PATH

## Assumptions

- System Python 3.13 is available in PATH
- `/c/csc/bin` can be in system PATH
- Tools are meant to be CLI utilities, not library modules
- No circular dependencies between tools

## Notes

- **Priority**: High — PATH and shell tools are critical infrastructure
- **Risk**: Medium — changing PATH could break other scripts. Test thoroughly.
- **Cleanup**: Remove all venv references from bin/
- **Documentation**: Update CLAUDE.md if shell tool usage changes

---

Use your best engineering judgment on:
- Which missing scripts to restore vs. stub
- How aggressive to be with PATH cleaning
- Whether to create wrapper scripts or refactor originals
- Shell profile location for PATH (test both Bash and PowerShell)

This is foundational tooling. Get it right so everything downstream works.

READY FOR IMPLEMENTATION
