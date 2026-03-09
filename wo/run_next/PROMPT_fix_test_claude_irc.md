# Task: Fix Failing Test — claude_irc

## What Failed

Test file: `tests/test_claude_irc.py`
Log file: `tests/logs/test_claude_irc.log`

### FAILED lines

```
tests/test_claude_irc.py::TestClaudeIRC::test_connect_to_claude_creates_client FAILED [  4%]
tests/test_claude_irc.py::TestClaudeIRC::test_connect_to_claude_failure_sets_client_none FAILED [  8%]
tests/test_claude_irc.py::TestClaudeIRC::test_connect_to_claude_initializes_empty_history FAILED [ 12%]
tests/test_claude_irc.py::TestClaudeIRC::test_input_handler_empty_input_skipped FAILED [ 16%]
tests/test_claude_irc.py::TestClaudeIRC::test_input_handler_plain_text_queries_model FAILED [ 20%]
tests/test_claude_irc.py::TestClaudeIRC::test_input_handler_say_command FAILED [ 24%]
tests/test_claude_irc.py::TestClaudeIRC::test_join_message_not_sent_to_model FAILED [ 28%]
tests/test_claude_irc.py::TestClaudeIRC::test_numeric_message_not_sent_to_model FAILED [ 32%]
tests/test_claude_irc.py::TestClaudeIRC::test_part_message_not_sent_to_model FAILED [ 36%]
tests/test_claude_irc.py::TestClaudeIRC::test_ping_no_model_query FAILED [ 40%]
tests/test_claude_irc.py::TestClaudeIRC::test_ping_sends_pong FAILED     [ 44%]
tests/test_claude_irc.py::TestClaudeIRC::test_privmsg_extracts_sender_and_text FAILED [ 48%]
tests/test_claude_irc.py::TestClaudeIRC::test_privmsg_pm_replies_to_target FAILED [ 52%]
tests/test_claude_irc.py::TestClaudeIRC::test_privmsg_reply_sent_to_channel FAILED [ 56%]
tests/test_claude_irc.py::TestClaudeIRC::test_privmsg_skips_own_messages FAILED [ 60%]
tests/test_claude_irc.py::TestClaudeIRC::test_privmsg_skips_own_messages_case_insensitive FAILED [ 64%]
tests/test_claude_irc.py::TestClaudeIRC::test_query_api_error_returns_empty FAILED [ 68%]
tests/test_claude_irc.py::TestClaudeIRC::test_query_appends_user_and_assistant_to_history FAILED [ 72%]
tests/test_claude_irc.py::TestClaudeIRC::test_query_empty_prompt_returns_empty FAILED [ 76%]
tests/test_claude_irc.py::TestClaudeIRC::test_query_history_capped_at_50_when_exceeding_100 FAILED [ 80%]
tests/test_claude_irc.py::TestClaudeIRC::test_query_no_client_returns_error FAILED [ 84%]
tests/test_claude_irc.py::TestClaudeIRC::test_query_returns_normal_reply FAILED [ 88%]
tests/test_claude_irc.py::TestClaudeIRC::test_query_sends_conversation_history FAILED [ 92%]
tests/test_claude_irc.py::TestClaudeIRC::test_query_server_change_directive FAILED [ 96%]
tests/test_claude_irc.py::TestClaudeIRC::test_query_state_persistence_directive FAILED [100%]
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_connect_to_claude_creates_client
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_connect_to_claude_failure_sets_client_none
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_connect_to_claude_initializes_empty_history
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_input_handler_empty_input_skipped
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_input_handler_plain_text_queries_model
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_input_handler_say_command
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_join_message_not_sent_to_model
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_numeric_message_not_sent_to_model
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_part_message_not_sent_to_model
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_ping_no_model_query - Im...
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_ping_sends_pong - Import...
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_privmsg_extracts_sender_and_text
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_privmsg_pm_replies_to_target
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_privmsg_reply_sent_to_channel
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_privmsg_skips_own_messages
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_privmsg_skips_own_messages_case_insensitive
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_query_api_error_returns_empty
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_query_appends_user_and_assistant_to_history
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_query_empty_prompt_returns_empty
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_query_history_capped_at_50_when_exceeding_100
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_query_no_client_returns_error
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_query_returns_normal_reply
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_query_sends_conversation_history
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_query_server_change_directive
FAILED tests/test_claude_irc.py::TestClaudeIRC::test_query_state_persistence_directive
```

## Instructions

1. Read the full log at `tests/logs/test_claude_irc.log`
2. Identify root cause of each failure
3. Fix the **code under test**, not the test (unless the test itself is wrong)
4. `rm tests/logs/test_claude_irc.log` (so cron re-runs the test)
5. Commit, push, move this prompt to done. **Do NOT run pytest yourself.**


--- Agent Log ---
COMPLETE

## Summary of changes

**Root cause**: All 25 tests failed because the `csc-claude` package was merged into `csc-service` but the test and source code weren't fully updated.

### 3 fixes applied:

1. **`tests/test_claude_irc.py`** — Updated import paths:
   - `csc_claude.claude` → `csc_service.clients.claude.claude`
   - `csc_client.client` → `csc_service.client.client`
   - Path additions updated from `packages/csc-claude`, `packages/csc-client`, `packages/csc-shared` → `packages/csc-service`

2. **`packages/csc-service/csc_service/shared/secret.py`** — Added missing functions:
   - `get_claude_api_key()` — reads from `ANTHROPIC_API_KEY` env var or `~/.config/csc-claude/secrets.json`
   - `get_claude_oper_credentials()` — reads oper credentials from config or env var
   - These were imported by `claude.py` but never defined (would cause `ImportError` at import time)

3. **`packages/csc-service/csc_service/clients/claude/claude.py`** — Fixed `handle_server_message`:
   - Removed double-processing bug: `_handle_privmsg_recv()` was called AND then the same query+send logic ran again, causing `assert_called_once` failures
   - Fixed PM reply target: was replying to `sender` instead of `target` for direct messages
   - Added display print before model query (was lost when removing `_handle_privmsg_recv` call)
[run_agent] Agent: opus, Root: C:\Users\davey\AppData\Local\Temp\csc\opus\repo
[run_agent] Starting Claude (claude-opus-4-6) for opus


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)
