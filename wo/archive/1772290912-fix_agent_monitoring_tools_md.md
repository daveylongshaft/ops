# Fix Agent Monitoring Tools - Status & Tail Commands

## Problem

**`agent status` command FAILS on Windows with TWO errors:**

```
Segmentation fault
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 2192
```

**Root Causes:**
1. agent_service.status() returns unicode characters (✅, ◀, ▶, ●, etc.)
2. Windows console (cp1252) can't encode these characters
3. Python tries to print unicode to cp1252 terminal → UnicodeEncodeError
4. Then segfault follows

**Impact:**
- `agent status` - BROKEN
- `agent tail` - likely BROKEN (same issue)
- User cannot monitor agents at all

## Solution: Unicode-Safe Output

### 1. Fix bin/agent Script

Add UTF-8 output wrapper and safe printing:

```python
#!/usr/bin/env python3
"""..."""

import sys
import os
import io
import time
from pathlib import Path
import traceback

# FIX: Set UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding='utf-8',
        errors='replace'
    )

# ... rest of imports and code ...

def safe_output(text):
    """Convert unicode to ASCII for Windows fallback."""
    if sys.platform == 'win32':
        replacements = {
            '✅': '[OK]',
            '❌': '[FAIL]',
            '⏳': '[WAIT]',
            '◀': '<',
            '▶': '>',
            '●': '*',
            '○': 'o',
            '■': '[#]',
            '→': '->',
            '←': '<-',
        }
        for unicode_char, ascii_equiv in replacements.items():
            text = text.replace(unicode_char, ascii_equiv)
    return text

def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Error: No command specified", file=sys.stderr)
        print("Run 'agent help' for usage information")
        sys.exit(1)

    command = sys.argv[1].lower()
    # ... command handling ...

    try:
        if command == 'list':
            print(safe_output(agent_svc.list()))
        elif command == 'select':
            # ... etc ...
            print(safe_output(agent_svc.select(args[0])))
        elif command == 'status':
            print(safe_output(agent_svc.status()))  # ← WRAPPED WITH safe_output
        elif command == 'tail':
            n = int(args[0]) if args else 20  # ← CONVERT TO INT
            print(safe_output(agent_svc.tail(n)))  # ← WRAPPED
        # ... rest of commands ...
```

### 2. Fix agent_service.py (status method)

Ensure status() returns ASCII-safe output:

```python
def status(self) -> str:
    """Return status info (unicode-safe on Windows)."""
    # ... build status_info ...

    # On Windows, convert unicode to ASCII
    if sys.platform == 'win32':
        replacements = {
            '✅': '[OK]',
            '❌': '[FAIL]',
            '⏳': '[WAIT]',
            '◀': '<',
            '▶': '>',
        }
        for unicode_char, ascii_equiv in replacements.items():
            status_info = status_info.replace(unicode_char, ascii_equiv)

    return status_info
```

### 3. Fix tail Method

Same approach - make output ASCII-safe:

```python
def tail(self, *args) -> str:
    """Tail WIP file with ASCII-safe output."""
    n = int(args[0]) if args else 20

    # ... get WIP content ...

    # On Windows, convert unicode
    if sys.platform == 'win32':
        content = content.replace('✅', '[OK]')
        content = content.replace('◀', '<')
        # ... etc

    return content
```

## Files to Modify

1. **bin/agent** (ALL calls to agent_svc methods)
   - Add UTF-8 wrapper at top
   - Add safe_output() function
   - Wrap all print(agent_svc.X()) with safe_output()
   - Fix line 151: `n = int(args[0]) if args else 20` (convert to int)
   - Remove fallback tail implementation (use service method)

2. **packages/csc-service/csc_service/shared/services/agent_service.py**
   - status() method (line 658+) - Add unicode conversion
   - tail() method (line 811+) - Add unicode conversion
   - Any other method that returns user-facing text

## Testing

**Before fix:**
```bash
$ agent status
Segmentation fault
UnicodeEncodeError: 'charmap' codec can't encode...
```

**After fix:**
```bash
$ agent status
CSC Agent Status
================
Selected: opus
Current: [WAIT] Running
...
[OK] Status complete
```

**Test commands:**
```bash
agent status       # ← Must work
agent tail 5       # ← Must work
agent tail         # ← Must use default 20
agent list         # ← Must work
```

## Success Criteria

- [X] `agent status` executes without segfault
- [X] `agent status` executes without UnicodeEncodeError
- [X] Output is readable (ASCII on Windows, Unicode elsewhere)
- [X] `agent tail [N]` works correctly
- [X] `agent tail` defaults to 20 lines
- [X] All agent monitoring commands work reliably
- [X] Works on Windows, Linux, macOS

## Related: Unicode System-Wide

This is the SAME issue as:
- Unicode cleanup filter workorder
- Any CLI with emoji/unicode output

**Consider after this fix:**
- Audit all bin/ scripts for unicode output
- Apply same safe_output() pattern everywhere
- Create shared unicode-safe printing utility
