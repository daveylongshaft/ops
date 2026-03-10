---
title: Review PR #2 in irc repo — bridge migration and service bug fixes
agent: opus
priority: high
---

# Review PR #2: Bridge Migration and Service Bug Fixes

## PR Link
https://github.com/daveylongshaft/irc/pull/2

## What to do
Review this PR on GitHub and either approve (gh pr review --approve) or request changes.

This is a bug-fix PR restoring broken services after the three-repo split.

## Context
The irc repo is at `/opt/csc/irc` (submodule). Review the PR diff focusing on:

1. **Bridge module migration** — `csc_service.bridge` was missing from irc repo after the three-repo split. csc-bridge.service has been crash-looping with ModuleNotFoundError. The bridge code was copied from `/opt/csc_old/`. Verify it's structurally intact and doesn't have import issues.

2. **help_service.py** — Class was `help` (lowercase) but the loader does `getattr(module, 'Help')` (capitalized). Also `self.server_instance` → `self.server`. Check that these match the `Service` base class pattern in `service.py`.

3. **server/main.py** — Added missing `main()` function. Entry point `/usr/local/bin/csc-server` imports `from csc_service.server.main import main`.

4. **gitignore** — runtime files excluded.

## Approve if
- Bridge module imports look clean and match old-codebase patterns
- help_service fix is correct
- main.py fix is correct

## Request changes if
- Any obvious bugs in migrated bridge code
- Import paths are wrong

