# Add Comprehensive Error Handling to Message Handlers

**Priority**: P1 (reliability)
**Estimate**: 3 hours
**Assignee**: gemini | jules | codex
**Reviewer**: anthropic (opus)

## Problem

The file `server_message_handler.py` (3,983 lines) has only 15 try/except blocks total. Most handler methods have NO error handling - exceptions bubble up and potentially crash the server or silently drop client messages.

## Objective

Add proper try/except error handling to all handler methods, ensuring:
1. No unhandled exceptions crash the server
2. Clients receive appropriate IRC error replies when operations fail
3. All errors are logged with context
4. No client data is silently dropped

## Context

**File**: `irc/packages/csc-service/csc_service/server/server_message_handler.py`
**Current state**: 15 try/except blocks across 3,983 lines
**Risk**: Server crashes, silent data loss, poor error visibility

**Examples of unprotected operations**:
- Dict lookups (KeyError)
- String parsing (IndexError, ValueError)
- File I/O (IOError)
- JSON operations (JSONDecodeError)
- Network operations (various exceptions)

## Implementation Pattern

Each handler method should follow this template:

```python
def _handle_command(self, msg, addr):
    """Handle COMMAND from client."""
    try:
        # Validation
        nick = self.client_registry.get(addr, {}).get("nick")
        if not nick:
            self._send(addr, ERR_NOTREGISTERED, ["COMMAND"], "You have not registered")
            return

        # Operation logic here
        # ...

    except KeyError as e:
        self.server.log(f"[ERROR] COMMAND handler KeyError from {addr}: {e}")
        self._send(addr, ERR_UNKNOWNERROR, ["COMMAND"], "Internal server error")
    except ValueError as e:
        self.server.log(f"[ERROR] COMMAND handler ValueError from {addr}: {e}")
        self._send(addr, ERR_NEEDMOREPARAMS, ["COMMAND"], "Invalid parameters")
    except Exception as e:
        self.server.log(f"[ERROR] COMMAND handler unexpected error from {addr}: {type(e).__name__}: {e}")
        self._send(addr, ERR_UNKNOWNERROR, ["COMMAND"], "Internal server error")
```

## Methods Requiring Error Handling

Add try/except to ALL handler methods (approximate line ranges):

**Registration handlers** (~300-600):
- `_handle_nick` - Nick validation, conflicts
- `_handle_user` - Registration state
- `_handle_pass` - Password validation

**Channel handlers** (~800-1400):
- `_handle_join` - Channel creation, bans, limits
- `_handle_part` - Member removal
- `_handle_topic` - Permissions, validation
- `_handle_names` - Channel iteration
- `_handle_list` - Channel enumeration

**Message handlers** (~1500-1800):
- `_handle_privmsg` - Routing, permissions
- `_handle_notice` - Delivery

**Mode handlers** (~1900-2400):
- `_handle_mode` - Complex parsing, validation
- `_handle_kick` - Permissions, member lookup

**Oper handlers** (~2500-3000):
- `_handle_oper` - Auth validation
- `_handle_kill` - Target lookup
- `_handle_setmotd` - File operations
- `_handle_stats` - Data collection

**Service handlers** (~3100-3500):
- `_handle_ai` - Service routing, parsing

**Info handlers** (~3600-3900):
- `_handle_whois` - User lookup
- `_handle_motd` - File reading

## Acceptance Criteria

- [ ] Every `_handle_*` method has try/except protection
- [ ] Specific exceptions caught where predictable (KeyError, ValueError, etc.)
- [ ] Generic Exception catch-all at the end of each handler
- [ ] All exceptions logged with context (command, addr, error type)
- [ ] Clients receive IRC error replies instead of timeouts
- [ ] Server remains stable when invalid input is sent
- [ ] Test with malformed IRC commands

## Files to Modify

- `irc/packages/csc-service/csc_service/server/server_message_handler.py`

## Testing

Create test cases for error conditions:

1. **Invalid commands**: Send garbage to server
2. **Missing parameters**: Send commands without required args
3. **Invalid nicks**: Use special chars, length violations
4. **Permission errors**: Non-ops try oper commands
5. **Resource errors**: Join channels that don't exist
6. **State errors**: Send commands before registration

Test script:
```python
# Send malformed IRC messages and verify:
# 1. Server doesn't crash
# 2. Error reply received
# 3. Error logged
```

## Notes

- Don't mask programming errors - log all exceptions
- Return specific IRC error codes when possible (ERR_NOSUCHNICK, etc.)
- ERR_UNKNOWNERROR is a fallback for unexpected errors
- Consider adding error metrics/counters for monitoring
- This is defensive programming - assume all inputs are malicious

## IRC Error Codes Reference

Already imported in the file:
- `ERR_NOTREGISTERED` - Client not registered yet
- `ERR_NEEDMOREPARAMS` - Missing required parameters
- `ERR_NOSUCHNICK` - Nick doesn't exist
- `ERR_NOSUCHCHANNEL` - Channel doesn't exist
- `ERR_NOPRIVILEGES` - Not authorized
- Add: `ERR_UNKNOWNERROR` - Generic internal error
