---
agent: haiku
platform: [linux, windows, android]
---

# Create dc-sh and Update dc-run

## Objective

Create `bin/dc-sh` as a bash-oriented Docker prompt runner, plus a Windows `.bat` wrapper. Update `bin/dc-run` to recognize `coding-agent` model shorthands.

## Files to Create

- `bin/dc-sh` — Python script, copy of `dc-run` with different defaults
- `bin/dc-sh.bat` — Windows batch wrapper

## Files to Modify

- `bin/dc-run` — add coding-agent shorthand support

## Task 1: Create `bin/dc-sh`

Copy `bin/dc-run` (201 lines) and change:

1. **Default agent/model** (lines ~37-38):
   ```python
   DEFAULT_AGENT = "coding-agent"
   DEFAULT_MODEL = "bash"
   ```

2. **Usage string** (line ~21 and ~157):
   ```
   Usage: dc-sh [list | menu | #number | filename] [--agent NAME] [--model MODEL]
   ```
   Update the default display to show `coding-agent (model: bash)`.

3. **Docstring** (top of file):
   ```python
   """
   Quick prompt runner for bash tasks — launches dc-agent-wrapper with coding-agent.

   Defaults to coding-agent with bash model. Use --model to override.
   Same interface as dc-run: list, menu, #N, filename.md
   """
   ```

4. Make executable: file should start with `#!/usr/bin/env python3` and have executable permissions.

Everything else (list_prompts, run_prompt, menu, main, arg parsing) stays identical — it's just a different default.

## Task 2: Create `bin/dc-sh.bat`

Windows batch wrapper, same pattern as existing `.bat` files in `bin/`:

```batch
@echo off
python "%~dp0dc-sh" %*
```

Check `bin/dc-run.bat` for the exact pattern used in this project and match it.

## Task 3: Update `bin/dc-run`

Add `coding-agent` as a recognized agent with model shorthands. In the usage text (around line 157-158), add:

```python
print("Agents: ollama-agent (local), claude (cloud), gemini (cloud), coding-agent (docker)")
```

No other changes needed to dc-run — it already supports `--agent coding-agent --model python3` via the flag parser.

## Reference Files

Read these before starting:
- `bin/dc-run` — the file to copy and modify
- `bin/dc-run.bat` — pattern for .bat wrapper
- `bin/coding-agent.bat` — another .bat example

## Work Log

Journal every step to this file using:
```bash
echo '<step>' >> prompts/wip/haiku-create-dc-sh-and-update-dc-run.md
```

## Success Criteria

- `dc-sh list` shows prompts (same as dc-run list)
- `dc-sh #1` launches with coding-agent/bash defaults
- `dc-sh task.md --model python3` overrides model
- `dc-sh.bat` works on Windows (calls dc-sh via python)
- `dc-run` usage text mentions coding-agent
- All files have proper shebang and are executable

STATUS: COMPLETE
