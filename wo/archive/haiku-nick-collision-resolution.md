---
requires: [python3, git]
platform: [windows, linux]
agent: haiku
---

# Nick Collision Detection & Resolution for Server Merges

## Objective

Implement automatic nick collision detection and resolution when CSC servers merge into a federated network.

## Problem Statement

When two independent CSC servers link together, they may have users with identical nicknames:
- Server A: User "alice" (connected at 12:00:00)
- Server B: User "alice" (connected at 12:05:00)

Result: **Nick collision** — which "alice" should win?

Solution: Deterministic collision resolution based on timestamps and server priority.

## Algorithm

### Step 1: Detect Collision

When S2S link is established:
```python
def detect_collision(local_nick: str, remote_server_nicks: List[str]) -> bool:
    """Check if local nick exists on remote server."""
    return local_nick.lower() in [n.lower() for n in remote_server_nicks]
```

### Step 2: Resolve Collision

```python
def resolve_collision(
    nick: str,
    local_connect_time: float,      # Unix timestamp
    remote_connect_time: float,     # Unix timestamp
    local_server_id: str,           # "server_001"
    remote_server_id: str           # "server_002"
) -> Tuple[str, str]:
    """
    Resolve collision between two nicks.

    Returns:
        (winner_server_id, loser_new_nick)
        Example: ("server_001", "alice_2")
    """

    # Rule 1: Earlier connection time wins
    if local_connect_time < remote_connect_time:
        winner = local_server_id
        loser_new = generate_collision_nick(nick, remote_server_id)
        return (winner, loser_new)

    elif remote_connect_time < local_connect_time:
        winner = remote_server_id
        loser_new = generate_collision_nick(nick, local_server_id)
        return (winner, loser_new)

    # Rule 2: If timestamps equal, use server ID as tiebreaker
    else:
        if local_server_id < remote_server_id:
            winner = local_server_id
            loser_new = generate_collision_nick(nick, remote_server_id)
        else:
            winner = remote_server_id
            loser_new = generate_collision_nick(nick, local_server_id)
        return (winner, loser_new)


def generate_collision_nick(original: str, server_id: str) -> str:
    """
    Generate new nick for collision loser.

    Examples:
        alice + server_002 → alice_s2
        bob + server_123 → bob_s123
    """
    # Extract server number from server_id ("server_001" → "1")
    server_num = server_id.split('_')[-1].lstrip('0') or '0'

    # Truncate original nick if needed to avoid exceeding max length (usually 30)
    max_suffix_len = len(f"_s{server_num}")
    max_original_len = 30 - max_suffix_len

    truncated = original[:max_original_len]
    return f"{truncated}_s{server_num}"
```

## Implementation

### File 1: `packages/csc-server/collision_resolver.py` (new)

```python
"""Nick collision detection and resolution for server merges."""

import hashlib
import time
from typing import Tuple, Dict
from pathlib import Path


class CollisionResolver:
    """Detect and resolve nick collisions in federated networks."""

    def __init__(self, local_server_id: str):
        self.local_server_id = local_server_id
        self.collision_log = []  # Track all resolutions for audit

    def detect_collision(self, nick: str, remote_nicks: list) -> bool:
        """Check if nick exists on remote server."""
        return nick.lower() in [n.lower() for n in remote_nicks]

    def resolve_collision(
        self,
        nick: str,
        local_connect_time: float,
        remote_connect_time: float,
        remote_server_id: str
    ) -> Tuple[str, str]:
        """
        Determine winner and loser nick in collision.

        Returns:
            (winner_server_id, loser_new_nick)
        """
        # Rule 1: Earlier connection time wins
        if abs(local_connect_time - remote_connect_time) > 1.0:  # 1 second threshold
            if local_connect_time < remote_connect_time:
                return (self.local_server_id, self._rename_nick(nick, remote_server_id))
            else:
                return (remote_server_id, self._rename_nick(nick, self.local_server_id))

        # Rule 2: Server ID tiebreaker (lexicographic)
        if self.local_server_id < remote_server_id:
            return (self.local_server_id, self._rename_nick(nick, remote_server_id))
        else:
            return (remote_server_id, self._rename_nick(nick, self.local_server_id))

    def _rename_nick(self, original: str, loser_server_id: str) -> str:
        """Generate new nick for collision loser."""
        server_num = loser_server_id.split('_')[-1].lstrip('0') or '0'
        max_suffix_len = len(f"_s{server_num}")
        max_original_len = 30 - max_suffix_len
        truncated = original[:max_original_len]
        new_nick = f"{truncated}_s{server_num}"
        return new_nick

    def log_collision(self, nick: str, winner: str, loser_nick: str):
        """Log collision resolution."""
        entry = {
            "timestamp": time.time(),
            "original_nick": nick,
            "winner_server": winner,
            "loser_new_nick": loser_nick
        }
        self.collision_log.append(entry)
```

### File 2: Extend `packages/csc-server/server_message_handler.py`

Add handler for KICK message to rename user:

```python
def handle_nick_collision(self, nick: str, new_nick: str, reason: str = "Nick collision"):
    """
    Send KICK message to user on collision, forcing nick change.

    Usage:
        :server KICK nick :Nick collision from server_002 - use new_nick_s2
    """
    # Send KICK to user
    kick_msg = format_irc_message(
        command="KICK",
        text=reason,
        nick=nick
    )
    self.server.send_to_client(nick, kick_msg)

    # Force disconnect and require re-register with new nick
    self.handle_quit(nick, reason)
```

### File 3: Extend `packages/csc-server/server.py`

Add collision resolver instance:

```python
from collision_resolver import CollisionResolver

class Server:
    def __init__(self, ...):
        # ... existing init ...
        self.collision_resolver = CollisionResolver(
            os.getenv("CSC_SERVER_ID", "server_001")
        )
```

## Integration with S2S (opus's work)

When `ServerLink` receives SYNCUSER message:

```python
def handle_syncuser(self, nick, host, server_id, connect_time, modes):
    """Handle SYNCUSER from remote server."""

    # Check for collision
    if self.server.has_user(nick):
        local_connect_time = self.server.users[nick]["connect_time"]
        winner, loser_nick = self.server.collision_resolver.resolve_collision(
            nick=nick,
            local_connect_time=local_connect_time,
            remote_connect_time=connect_time,
            remote_server_id=server_id
        )

        if winner == self.server.server_id:
            # We won, tell remote server to rename their user
            self.send_message(f"RENAMENICK {nick} {loser_nick}")
            self.server.log(f"Nick collision: {nick} - remote user renamed to {loser_nick}")
        else:
            # We lost, rename our local user
            self.server.rename_user(nick, loser_nick)
            self.server.log(f"Nick collision: {nick} - local user renamed to {loser_nick}")

    # Now add remote user
    self.server.add_remote_user(nick, host, server_id, modes)
```

## Testing

### Unit Tests: `tests/test_collision_resolver.py`

```python
from csc_server.collision_resolver import CollisionResolver

def test_earlier_connection_wins():
    resolver = CollisionResolver("server_001")
    winner, loser = resolver.resolve_collision(
        nick="alice",
        local_connect_time=100.0,   # Earlier
        remote_connect_time=200.0,  # Later
        remote_server_id="server_002"
    )
    assert winner == "server_001"
    assert loser == "alice_s2"

def test_server_id_tiebreaker():
    resolver = CollisionResolver("server_001")
    winner, loser = resolver.resolve_collision(
        nick="bob",
        local_connect_time=100.0,
        remote_connect_time=100.0,  # Same time
        remote_server_id="server_002"
    )
    assert winner == "server_001"  # server_001 < server_002 lexicographically

def test_nick_renaming():
    resolver = CollisionResolver("server_001")
    new_nick = resolver._rename_nick("alice", "server_002")
    assert new_nick == "alice_s2"
```

### Integration Tests: `tests/test_collision_integration.py`

- Start 2 servers with same username
- Simulate S2S link
- Verify collision detected
- Verify one user renamed
- Verify both can coexist after rename

## Deliverables

- [ ] `CollisionResolver` class implemented
- [ ] `detect_collision()` method works
- [ ] `resolve_collision()` uses correct algorithm
- [ ] Nick renaming generates valid IRC nicks
- [ ] Unit tests pass
- [ ] Integration with S2S (work with opus)
- [ ] Audit log tracks all collisions
- [ ] Commit: "Implement nick collision detection and resolution"

## Files

- Create: `packages/csc-server/collision_resolver.py`
- Modify: `packages/csc-server/server.py`
- Modify: `packages/csc-server/server_message_handler.py`
- Create: `tests/test_collision_resolver.py`
- Create: `tests/test_collision_integration.py`

## References

- RFC 2812 Section 2.3.1 — Nickname rules
- Server linking prompt (opus): `opus-server-linking-federation.md`
--- RESTART Thu, Feb 19, 2026  1:41:35 PM ---
AGENT_PID: 1004
