---
requires: [python3, git]
platform: [linux]
---
# Fix: Platform CLI flags not wired up

## Problem

The Platform layer (`packages/csc_shared/platform.py`) has `configure_install_mode(install_at_startup, install_as_needed)` but NO entry point actually parses `--install-packages-at-startup` or `--install-as-needed` from sys.argv. The flags are dead code.

## What needs to happen

### 1. Add argparse to entry points

These files need `argparse` added to parse the two flags:

- `packages/csc_server/main.py` — server entry point
- `packages/csc-claude/main.py` — Claude client entry point
- `packages/csc-gemini/main.py` — Gemini client entry point (if it exists)
- `packages/csc-chatgpt/main.py` — ChatGPT client entry point (if it exists)
- `packages/coding-agent/coding_agent/cli.py` — coding agent CLI

Each entry point should:
1. Parse `--install-packages-at-startup` and `--install-as-needed` / `-as-needed` flags
2. After constructing the object (Server/Claude/etc), call `obj.configure_install_mode(...)` before `obj.run()`
3. Unknown args should be ignored (use `parse_known_args`) so existing usage isn't broken

### 2. Write tests that actually catch the gap

Create `tests/test_platform_flags.py` with tests that:

- Verify `configure_install_mode()` sets the internal flags correctly
- Verify that each entry point's `main()` function accepts the flags without crashing (mock the actual run)
- Verify that passing `--install-packages-at-startup` results in `_install_at_startup == True` on the constructed object
- Verify that passing `--install-as-needed` results in `_install_as_needed == True`
- Verify that passing NO flags leaves both False (default behavior = inventory only)
- Test that invalid/unknown flags don't crash the entry point

### 3. Delete stale test log

```bash
rm tests/logs/test_platform_flags.log
```

So cron picks it up.

## Files to modify

- `packages/csc_server/main.py`
- `packages/csc-claude/main.py`
- Any other client main.py files that exist
- `packages/coding-agent/coding_agent/cli.py`

## Files to create

- `tests/test_platform_flags.py`

## Verification

After your changes, this should work without error:
```bash
python packages/csc_server/main.py --install-packages-at-startup --help  # should show the flag
python packages/csc_server/main.py --install-as-needed --help
```
