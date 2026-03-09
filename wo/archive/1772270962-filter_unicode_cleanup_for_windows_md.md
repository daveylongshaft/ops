# Unicode Cleanup Filter for Windows MSYS2

## Problem

On Windows MSYS2, markdown files with unicode characters cause encoding errors:

```
Error: 'charmap' codec can't encode character '\u2192' in position 361
```

This breaks:
- `wo read` command
- File parsing
- Terminal display
- Agent processing

## Solution

Create a Unicode-to-ASCII filter that:
1. Strips all unicode arrows, emojis, symbols
2. Replaces with plain ASCII equivalents
3. Keeps file readable and professional
4. Works on any .md file
5. Preserves semantic meaning

## Character Replacement Map

### Arrows
```
→  becomes  ->
←  becomes  <-
↑  becomes  ^
↓  becomes  v
⇒  becomes  =>
⇐  becomes  <=
↔  becomes  <->
```

### Status/Check marks
```
✅  becomes  [OK]
✓   becomes  [YES]
✔   becomes  [CHECK]
✘   becomes  [NO]
✗   becomes  [NO]
❌  becomes  [FAIL]
⚠   becomes  [WARN]
⚡  becomes  [ALERT]
```

### Emojis/Symbols
```
🚀  becomes  >>
🔴  becomes  [RED]
🟡  becomes  [YELLOW]
🟢  becomes  [GREEN]
🟠  becomes  [ORANGE]
◀   becomes  <
▶   becomes  >
■   becomes  [BLOCK]
●   becomes  *
○   becomes  o
```

### Misc Symbols
```
•   becomes  -
…   becomes  ...
–   becomes  -
—   becomes  --
★   becomes  *
☐   becomes  [ ]
☑   becomes  [X]
☒   becomes  [X]
```

## Implementation

Create `bin/unicode-cleanup.py`:

```python
#!/usr/bin/env python3
"""
Strip unicode characters from markdown files for Windows MSYS2 compatibility.
Replaces arrows, emojis, symbols with plain ASCII equivalents.
"""

import sys
from pathlib import Path

REPLACEMENTS = {
    # Arrows
    '→': '->',
    '←': '<-',
    '↑': '^',
    '↓': 'v',
    '⇒': '=>',
    '⇐': '<=',
    '↔': '<->',
    # Status marks
    '✅': '[OK]',
    '✓': '[YES]',
    '✔': '[CHECK]',
    '✘': '[NO]',
    '✗': '[NO]',
    '❌': '[FAIL]',
    '⚠': '[WARN]',
    '⚡': '[ALERT]',
    # Emojis
    '🚀': '>>',
    '🔴': '[RED]',
    '🟡': '[YELLOW]',
    '🟢': '[GREEN]',
    '🟠': '[ORANGE]',
    # Shapes
    '◀': '<',
    '▶': '>',
    '■': '[BLOCK]',
    '●': '*',
    '○': 'o',
    # Misc
    '•': '-',
    '…': '...',
    '–': '-',
    '—': '--',
    '★': '*',
    '☐': '[ ]',
    '☑': '[X]',
    '☒': '[X]',
}

def cleanup_unicode(text):
    """Replace unicode chars with ASCII equivalents."""
    for unicode_char, ascii_equiv in REPLACEMENTS.items():
        text = text.replace(unicode_char, ascii_equiv)
    return text

def main():
    if len(sys.argv) < 2:
        print("Usage: unicode-cleanup.py <file.md> [<file2.md> ...]")
        sys.exit(1)

    for filepath in sys.argv[1:]:
        path = Path(filepath)
        if not path.exists():
            print(f"Error: {filepath} not found")
            continue

        try:
            content = path.read_text(encoding='utf-8')
            cleaned = cleanup_unicode(content)

            if content != cleaned:
                path.write_text(cleaned, encoding='utf-8')
                print(f"Cleaned: {filepath}")
            else:
                print(f"OK: {filepath} (no unicode)")

        except Exception as e:
            print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    main()
```

## Integration Points

### 1. Pre-write Hook (Agents Creating Files)

When agents write markdown files via Edit/Write, filter should run:

```python
# In Write tool or Edit tool
content = cleanup_unicode(content)
path.write_text(content, encoding='utf-8')
```

### 2. Post-read Hook (Reading Files)

Display filter on `wo read`:

```python
# In workorders service read
content = path.read_text(encoding='utf-8', errors='replace')
# Keep unicode in file, but display safe
```

Actually, keep unicode in files (UTF-8 stored fine). Just:
- Strip it from **created files** (agents should generate ASCII)
- Add to `.gitignore` any `.unicode-backup` files

### 3. Cleanup Script (Manual)

```bash
# Clean all existing markdown files
python bin/unicode-cleanup.py workorders/**/*.md
python bin/unicode-cleanup.py **/*.md --recursive
```

## Files to Clean

After implementation:
- All workorders (ready/, wip/, done/, hold/)
- All .md files in project root
- All documentation files
- Agent-generated markdown

## Testing

1. Create test .md with unicode:
   ```
   ✅ Done -> work
   🚀 Launch [RED]
   ```

2. Run filter:
   ```bash
   python bin/unicode-cleanup.py test.md
   ```

3. Verify output:
   ```
   [OK] Done -> work
   >> Launch [RED]
   ```

4. Run `wo read test.md` - should work without charset errors

## Success Criteria

- [X] `bin/unicode-cleanup.py` created
- [X] All REPLACEMENTS map defined
- [X] All existing .md files cleaned
- [X] `wo read` works on all files without charset errors
- [X] No regression: content still readable and professional
- [X] Agents generate ASCII-only in future workorders
