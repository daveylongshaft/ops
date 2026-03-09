---
requires: [python3, git]
platform: [linux]
---
# Wire Platform Install Mode CLI Flags to Entry Points

## Recommended Agent: gemini-2.5-pro (moderate complexity, code changes across files)

## Goal
Add argparse to all entry points so `--install-packages-at-startup` and `--install-as-needed` flags actually work.

## Background
The Platform class has `configure_install_mode()` but no entry point parses the flags. They're dead code.

## Steps

1. Read each entry point:
   - `packages/csc_server/main.py`
   - `packages/csc-claude/main.py`
   - `packages/csc-gemini/main.py`
   - `packages/csc-chatgpt/main.py`
   - `packages/coding-agent/coding_agent/cli.py`

2. Add argparse to each (use `parse_known_args` to not break existing usage):
   ```python
   import argparse
   parser = argparse.ArgumentParser()
   parser.add_argument('--install-packages-at-startup', action='store_true')
   parser.add_argument('--install-as-needed', action='store_true')
   args, _ = parser.parse_known_args()
   ```

3. After constructing the object, call:
   ```python
   obj.configure_install_mode(
       install_at_startup=args.install_packages_at_startup,
       install_as_needed=args.install_as_needed
   )
   ```

4. Delete stale test log: `rm tests/logs/test_platform_flags.log`
5. Commit, push

## Files to modify
- `packages/csc_server/main.py`
- `packages/csc-claude/main.py`
- `packages/csc-gemini/main.py`
- `packages/csc-chatgpt/main.py`
- `packages/coding-agent/coding_agent/cli.py`

## See also
- `prompts/ready/PROMPT_fix_platform_cli_flags.md` (existing prompt with more detail)
