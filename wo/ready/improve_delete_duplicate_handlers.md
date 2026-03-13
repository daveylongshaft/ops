# Delete Duplicate Handler Methods

**Priority**: P1 (bug fix)
**Estimate**: 30 minutes
**Assignee**: gemini | jules | codex
**Reviewer**: anthropic (opus)

## Problem

Four methods in `server_message_handler.py` are defined TWICE, causing ambiguity and potential bugs. When a method is defined multiple times in Python, only the last definition is used - the earlier ones are silently ignored.

## Objective

Find and delete the first occurrence of each duplicate method, keeping only the second (most recent) definition.

## Context

**File**: `irc/packages/csc-service/csc_service/server/server_message_handler.py`
**Issue**: Duplicate method definitions

## Duplicate Methods (Line Numbers)

Based on grep analysis, these methods appear twice:

1. **_handle_setmotd**
   - First occurrence: Line 1954
   - Second occurrence: Line 3497
   - **Action**: Delete lines 1954-1980 (first definition)

2. **_handle_stats**
   - First occurrence: Line 1981
   - Second occurrence: Line 3704
   - **Action**: Delete lines 1981-2038 (first definition)

3. **_handle_rehash**
   - First occurrence: Line 2039
   - Second occurrence: Line 3750
   - **Action**: Delete lines 2039-2045 (first definition)

4. **_handle_shutdown**
   - First occurrence: Line 2046
   - Second occurrence: Line 3757
   - **Action**: Delete lines 2046-2060 (first definition)

## Implementation Steps

1. Open `irc/packages/csc-service/csc_service/server/server_message_handler.py`
2. For each duplicate method:
   - Locate the FIRST occurrence (earlier line number)
   - Read both definitions to verify they are duplicates
   - If implementations differ, choose the more complete/recent one
   - Delete the first occurrence
3. Verify no other duplicate methods exist:
   ```bash
   # Use this command to find duplicates:
   grep -n "^    def " server_message_handler.py | awk -F: '{print $2}' | sort | uniq -d
   ```
4. Test that all IRC commands still work

## Acceptance Criteria

- [ ] All four duplicate methods removed
- [ ] Only one definition remains for each method
- [ ] No syntax errors after deletion
- [ ] Server starts successfully
- [ ] IRC commands SETMOTD, STATS, REHASH, SHUTDOWN still function
- [ ] No other duplicate methods remain in the file

## Files to Modify

- `irc/packages/csc-service/csc_service/server/server_message_handler.py`

## Testing

After making changes:
1. Start the IRC server
2. Connect with an IRC client
3. Test each command:
   - `/oper admin changeme` (authenticate as oper)
   - `/stats` (should show server statistics)
   - `/quote SETMOTD Test MOTD` (should update MOTD)
   - Verify REHASH and SHUTDOWN commands exist (don't actually run SHUTDOWN)

## Notes

- This is a simple cleanup task but important for code correctness
- Python silently ignores earlier definitions when methods are duplicated
- The duplicate definitions suggest copy-paste errors during development
- Line numbers may shift slightly after each deletion - work from top to bottom
