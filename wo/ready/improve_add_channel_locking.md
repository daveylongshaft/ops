# Add Thread-Safe Locking to ChannelManager

**Priority**: P2 (reliability)
**Estimate**: 2 hours
**Assignee**: gemini | jules | codex
**Reviewer**: anthropic (opus)

## Problem

The `ChannelManager` class has no thread synchronization despite being accessed concurrently by multiple UDP message handlers. The code explicitly documents "Not thread-safe. Caller must synchronize access" (line 70 in channel.py), but callers don't actually synchronize, creating race conditions.

## Objective

Add proper thread-safe locking to ChannelManager using Python's `threading.RLock()` to prevent race conditions during concurrent channel/member operations.

## Context

**File**: `irc/packages/csc-service/csc_service/shared/channel.py`
**Current state**: No locking mechanism exists
**Risk**: Race conditions on channel creation, member add/remove, mode changes

**Evidence of concurrent access**:
- MessageHandler processes UDP messages in parallel
- Multiple clients can JOIN/PART channels simultaneously
- Channel member lists can be corrupted by race conditions

## Implementation Steps

1. Add RLock import to channel.py:
   ```python
   import threading
   ```

2. Add lock instance variable to ChannelManager.__init__():
   ```python
   def __init__(self):
       self.channels: Dict[str, Channel] = {}
       self._lock = threading.RLock()  # Add this line
       self.ensure_channel(self.DEFAULT_CHANNEL)
   ```

3. Wrap all multi-step operations with lock acquisition:
   - `ensure_channel()` - Channel creation is read-then-write
   - `get_channel()` - Can race with channel deletion
   - `remove_channel()` - Must atomically check empty and delete
   - `list_channels()` - Iteration needs consistent snapshot
   - `find_user_in_channels()` - Multi-channel search must be atomic

4. Example locking pattern:
   ```python
   def ensure_channel(self, name: str) -> Channel:
       with self._lock:
           lower_name = name.lower()
           if lower_name not in self.channels:
               self.channels[lower_name] = Channel(name)
           return self.channels[lower_name]
   ```

5. Document thread-safety guarantees in class docstring

## Methods Requiring Lock Protection

From `irc/packages/csc-service/csc_service/shared/channel.py`:

- Line ~510: `__init__()` - Add lock initialization
- Line ~530: `ensure_channel()` - Wrap entire method
- Line ~545: `get_channel()` - Wrap dict access
- Line ~560: `remove_channel()` - Wrap entire method (check-then-delete)
- Line ~575: `list_channels()` - Wrap dict iteration
- Line ~590: `find_user_in_channels()` - Wrap multi-channel iteration

## Acceptance Criteria

- [ ] RLock added to ChannelManager class
- [ ] All public methods protected by lock
- [ ] No deadlock scenarios introduced
- [ ] Documentation updated to reflect thread-safety
- [ ] Manual testing with concurrent channel operations
- [ ] No performance regression (RLock is reentrant, allows recursive calls)

## Files to Modify

- `irc/packages/csc-service/csc_service/shared/channel.py` - Add locking to ChannelManager

## Testing

1. Start server
2. Connect multiple IRC clients simultaneously
3. Have all clients JOIN the same channel at once
4. Rapidly PART and rejoin channels
5. Check channel member lists for consistency
6. Monitor for any race condition errors in logs

Stress test:
```python
# Create test script that spawns 10 threads
# Each thread joins/parts #test 100 times
# Verify final channel state is consistent
```

## Notes

- Use RLock (reentrant lock) not Lock - allows same thread to acquire multiple times
- ChannelManager is already a singleton accessed by multiple handlers
- This fix prevents rare but serious data corruption bugs
- Consider adding lock timeout logging for debugging deadlock scenarios
- Performance impact should be minimal (locks held for microseconds)

## Why RLock vs Lock

RLock (reentrant lock) allows the same thread to acquire the lock multiple times, which is important if one ChannelManager method calls another. Regular Lock would deadlock in this scenario.
