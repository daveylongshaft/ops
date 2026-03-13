# Generate 9 Improvement Workorders

Create 9 separate workorder files in ops/wo/ready/ for the following improvements to the CSC IRC codebase. Each workorder should have enough context to be independently assignable to gemini, jules, or codex.

## The 9 Improvements

1. **Split server_message_handler.py** - Break the 3,983-line monolith into 6-7 files by concern (registration, channels, modes, services, admin). One class per file per project policy.

2. **Delete duplicate handlers** - `_handle_setmotd`, `_handle_stats`, `_handle_rehash`, `_handle_shutdown` each appear TWICE in server_message_handler.py. Find and delete the duplicates.

3. **Add locking to ChannelManager** - No locks on concurrent channel/member operations. Add RLock to ChannelManager, wrap multi-step operations.

4. **Error handling gaps** - Only 3 try/except in 3,983 lines of server_message_handler.py. Add proper error handling to all handler methods, never silently drop data.

5. **Fix emoji in logs** - `self.server.log()` calls use unicode emoji (violates ASCII-only .md policy). Replace all emoji with ASCII equivalents like [BLOCKED], [OK], etc.

6. **Structured logging** - Replace free-form log strings with structured fields (timestamp, level, operation, user, result). Add log rotation.

7. **Config schema validation** - 8+ JSON config files in etc/ with no validation. Add schema validation on load, versioning, graceful error on corrupt files.

8. **Startup health checks** - Add port conflict detection, JSON validity check, dependency verification on server start.

9. **Test coverage improvements** - Add unit test isolation with mocking, pytest fixtures for common setup, coverage metrics via pytest-cov.

## Instructions

- Create each as a separate .md file in ops/wo/ready/
- Filename format: `improve_<short_name>.md`
- Each workorder should reference the exact files and line numbers where changes are needed
- Keep workorders focused - one concern per file
- Tag for assignment to: gemini, jules, or codex
- PRs will be reviewed by anthropic (opus) in pr-review role
START 2026-03-13 04:49:42 PID:42428
Reading task requirements and exploring codebase structure
Verified issues: duplicates at lines 1954/3497, 1981/3704, 2039/3750, 2046/3757; emoji found; 15 try blocks
Creating workorder 1: Split server_message_handler.py
Creating workorder 2: Delete duplicate handlers
Creating workorder 3: Add locking to ChannelManager
Creating workorder 4: Add error handling
