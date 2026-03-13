# Split server_message_handler.py into Multiple Files

**Priority**: P2
**Estimate**: 4 hours
**Assignee**: gemini | jules | codex
**Reviewer**: anthropic (opus)

## Problem

The file `irc/packages/csc-service/csc_service/server/server_message_handler.py` is a 3,983-line monolith that violates the project's "one class per file" policy. It contains multiple handler categories (registration, channels, modes, services, admin) all in a single MessageHandler class.

## Objective

Break the monolithic MessageHandler class into 6-7 focused files, each handling a distinct concern, following the project's one-class-per-file policy.

## Context

**Current file**: `irc/packages/csc-service/csc_service/server/server_message_handler.py`
**Line count**: 3,983 lines
**Policy violation**: Multiple logical concerns in one class

**Project policy** (from MEMORY.md):
- One class per file
- File named after the class (snake_case)
- Example: `data.py` contains only `class Data`

## Proposed Split

Create 7 new files in `irc/packages/csc-service/csc_service/server/handlers/`:

1. **registration_handler.py** - `class RegistrationHandler`
   - Methods: `_handle_nick`, `_handle_user`, `_handle_pass`, `_handle_ping`, `_handle_pong`, `_handle_quit`
   - Registration state machine
   - Approx 400-500 lines

2. **channel_handler.py** - `class ChannelHandler`
   - Methods: `_handle_join`, `_handle_part`, `_handle_names`, `_handle_list`, `_handle_topic`, `_handle_invite`
   - Channel membership operations
   - Approx 600-700 lines

3. **message_handler.py** - `class MessageRoutingHandler`
   - Methods: `_handle_privmsg`, `_handle_notice`
   - Message routing and delivery
   - Approx 300-400 lines

4. **mode_handler.py** - `class ModeHandler`
   - Methods: `_handle_mode`, `_handle_kick`, `_handle_away`
   - User and channel modes
   - Approx 500-600 lines

5. **oper_handler.py** - `class OperHandler`
   - Methods: `_handle_oper`, `_handle_kill`, `_handle_wallops`, `_handle_setmotd`, `_handle_stats`, `_handle_rehash`, `_handle_shutdown`
   - Operator-only commands
   - Approx 400-500 lines

6. **service_handler.py** - `class ServiceHandler`
   - Methods: `_handle_ai`, service command routing
   - IRC service integration
   - Approx 300-400 lines

7. **info_handler.py** - `class InfoHandler`
   - Methods: `_handle_motd`, `_handle_whois`, `_handle_whowas`, `_handle_who`, `_handle_userhost`, `_handle_ison`
   - Information/query commands
   - Approx 400-500 lines

## Implementation Steps

1. Create directory `irc/packages/csc-service/csc_service/server/handlers/`
2. Create `__init__.py` in handlers directory
3. Extract each handler category into its own file with proper imports
4. Create a new slimmed-down `message_handler.py` (main dispatcher) that:
   - Imports all specialized handlers
   - Routes commands to appropriate handler
   - Maintains backward compatibility
5. Update imports in `server.py` and other files that use MessageHandler
6. Verify all IRC commands still work (test with manual client connection)
7. Update documentation to reflect new structure

## Acceptance Criteria

- [ ] 7 new handler files created in `handlers/` subdirectory
- [ ] Each file contains exactly one class
- [ ] All IRC commands still function identically
- [ ] No code duplication between files
- [ ] All imports updated and working
- [ ] Main `server_message_handler.py` reduced to <500 lines (dispatcher only)
- [ ] No functionality regressions

## Files to Modify

- `irc/packages/csc-service/csc_service/server/server_message_handler.py` - Split this file
- `irc/packages/csc-service/csc_service/server/server.py` - Update MessageHandler imports
- Create: `irc/packages/csc-service/csc_service/server/handlers/*.py` - 7 new files

## Testing

- Manual IRC client connection test
- Test registration flow (NICK/USER/PASS)
- Test channel operations (JOIN/PART/PRIVMSG)
- Test oper commands (OPER/KILL)
- Test service commands (AI)
- Test info commands (WHOIS/MOTD)

## Notes

- Preserve all existing functionality - this is a refactor, not a rewrite
- Keep method signatures identical for backward compatibility
- Shared utilities can go in a `handlers/utils.py` file if needed
- This will make the codebase much easier to navigate and maintain
