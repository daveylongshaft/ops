# Task: Ghost Nick Cleanup — last_seen Expiry + Test Teardown

## Problem

Ghost nicks accumulate in `channels.json` because:
1. Tests never send QUIT — nicks persist on disk across restarts
2. Server startup loads channel members from disk but doesn't check if they're actually connected
3. `_run_cleanup_once()` only checks `self.clients` (in-memory) — it never prunes persisted channel members who have no live connection

Result: ~28 test nicks (whoischecker, pmalice, operuser, etc.) permanently stuck in #general.

## Fix: Three Parts

### 1. Server: prune stale channel members using last_seen

The `users.json` already tracks `last_seen` timestamps per user. On the cleanup cycle (`_run_cleanup_once()`), ALSO check persisted channel members:

- For each channel member nick, check if that nick exists in `self.clients` (live connection)
- If NOT live, check `users.json` last_seen timestamp
- If `last_seen` exceeds the ping-pong timeout (`self.timeout`), run the full quit path: call `_server_kill(nick, "Stale session expired")` to remove from channels, user reg, and persist
- This handles ghosts from tests, crashed clients, and any other source

Location: `server.py:_run_cleanup_once()` — add a second pass after the existing live-client check:

```python
# Second pass: prune persisted channel members with no live connection
for channel_name in self.channel_manager.list_channels():
    ch = self.channel_manager.get(channel_name)
    for nick in list(ch.members.keys()):
        # Skip if nick has a live connection
        if self._find_client_by_nick(nick):
            continue
        # Check last_seen from users.json
        user = self.client_registry.get(nick, {})
        last_seen = user.get("last_seen", 0)
        if now - last_seen > self.timeout:
            self.log(f"[CLEANUP] Pruning stale channel member {nick} from {channel_name}")
            # Remove from channel and persist
            ch.members.pop(nick, None)
            pruned = True
    if pruned:
        self.channel_manager.persist()
```

### 2. Server startup: immediate prune on boot

Run one cleanup pass right after `storage.restore_all()` in `run()` or `__init__`. Since no clients are connected at startup, any channel member whose `last_seen` exceeds timeout gets pruned immediately. This catches ghosts left from before the previous shutdown.

### 3. Tests: send QUIT in teardown

Every test that creates UDP clients must send `QUIT :test done\r\n` before closing sockets. This prevents NEW ghosts from accumulating.

Pattern for all test teardowns:
```python
def tearDown(self):
    for sock in self.sockets:
        try:
            sock.sendto(b'QUIT :test done\r\n', self.server_addr)
            time.sleep(0.05)  # brief pause for server to process
        except:
            pass
        sock.close()
```

Files to update:
- `tests/test_server_irc.py`
- `tests/test_integration.py`
- `tests/test_topic_command.py`
- `tests/test_persistence.py`
- Any other test with UDP client sockets

## Key Files

- `packages/csc-server/server.py` — `_run_cleanup_once()`, `run()`, `__init__`
- `packages/csc-server/users.json` — has `last_seen` per user
- `packages/csc-server/channels.json` — has stale members to prune
- `tests/test_*.py` — add QUIT to teardown

## Instructions

1. Read `server.py:_run_cleanup_once()` and understand the existing cleanup
2. Add the persisted-member prune pass using last_seen
3. Add startup prune call
4. Update test teardowns to send QUIT
5. Do NOT run tests — cron handles that
6. Delete stale test logs so cron retests
7. Commit, push, move to done
Reading tools/INDEX.txt and tools/csc-server.txt to locate server.py and cleanup methods
Reading packages/csc-server/server.py to locate _run_cleanup_once and run methods
Reading test files to identify where to add QUIT in tearDown
Modifying packages/csc-server/server.py to add ghost nick cleanup logic
Updating server.py __init__ to run cleanup on startup
Updating make_client in tests/test_integration.py to send QUIT on teardown


--- Agent Log ---
python: can't open file 'C:\\Users\\davey\\AppData\\Local\\Temp\\csc\\gemini-2.5-pro\\repo\\agents\\gemini-2.5-pro\\bin\\run_agent.py': [Errno 2] No such file or directory


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)
