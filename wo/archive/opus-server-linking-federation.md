---
requires: [python3, git]
platform: [windows, linux]
agent: opus
---

# Server Linking & Federation System for CSC

## Objective

Implement a server-to-server (S2S) linking protocol that allows multiple CSC IRC servers to connect, synchronize channels and users, pass traffic between networks, and handle nick collisions on server merges.

## Background

The CSC project currently runs single IRC servers. The goal is to enable a **federated network** where:
- Multiple CSC servers can link and form a network
- Channels are synchronized across linked servers
- Client/user traffic passes between networks
- Nick collisions are detected and resolved

## High-Level Design

### 1. Server-to-Server Protocol

```
SERVER 1 (facingaddictionwithhope.com)
        ↓ (S2S Connection)
SERVER 2 (another.csc.server)
        ↓ (S2S Connection)
SERVER 3 (third.csc.server)
```

**S2S Messages (new IRC commands):**
- `SLINK <password>` — Request server link
- `SLINKACK <timestamp>` — Acknowledge link
- `SYNCUSER <nick> <host> <modes>` — Sync user across servers
- `SYNCCHAN <channel> <modes> <members>` — Sync channel state
- `SYNCMSG <source> <target> <text>` — Pass message between servers
- `DESYNC <nick|channel>` — Remove nick/channel from remote

### 2. Nick Collision Resolution

When servers merge and find duplicate nicks:
1. **Server timestamp comparison** — Older connection wins, newer gets RENAME
2. **Hash-based tiebreaker** — (hash(nick) + hash(server)) % 2
3. **Oper override** — Oper can force rename

**Collision message:**
```
:server1 KICK nick :Nick collision from server2 - use new_nick_12345
```

### 3. Time Synchronization

- Each server has a **canonical timestamp** from startup
- S2S links exchange timestamps on connect
- If time drift > 10 seconds, log warning and use server with lower ID
- Use NTP time from platform.json if available

### 4. Channel Synchronization

When a server joins the network:
1. **Fetch all channels** from peer servers via `CHANNELLIST`
2. **Merge channel members** using sorted nick list
3. **Apply channel modes** from primary server (lowest ID)
4. **Replay recent history** (last 100 messages per channel)

## Implementation Requirements

### Part A: Core S2S Protocol (PRIORITY)

**File: `packages/csc-server/server_s2s.py`**
- `class ServerLink` — Represents a connection to another CSC server
  - `__init__(local_server, remote_host, remote_port, password)`
  - `connect()` — Establish TCP connection to remote server
  - `authenticate()` — Exchange SLINK/SLINKACK handshake
  - `send_message(command, *args)` — Send S2S command
  - `receive_message()` — Receive and parse S2S command
  - `is_connected()` — Check connection status
  - `close()` — Gracefully close link

- `class ServerNetwork` — Manages all linked servers
  - `__init__(local_server)`
  - `link_to(host, port, password)` — Initiate link
  - `get_peer_servers()` — List all linked servers
  - `broadcast_to_network(command, exclude_server=None)` — Send to all peers
  - `get_user_from_network(nick)` — Find user on any server in network
  - `get_channel_from_network(channel)` — Find channel on any server

### Part B: Channel & User Synchronization

**File: `packages/csc-server/server_message_handler.py` (extend)**
- Add handlers for S2S sync commands
- When user JOINs locally: broadcast `SYNCUSER` to network
- When user PRIVMSG: if target is on remote server, route via `SYNCMSG`
- When channel MODE changes: broadcast `SYNCCHAN` to peers

**File: `packages/csc-server/server.py` (extend)**
- Track which users/channels are from which servers
- Metadata: `users[nick]["remote_server"] = "server2"`
- Metadata: `channels[channel]["sync_servers"] = ["server1", "server2"]`

### Part C: Nick Collision Handling

**File: `packages/csc-server/collision_resolver.py`** (new)
- `detect_collision(nick, local_server, remote_server)` → bool
- `resolve_collision(nick, local_server, remote_server)` → (winner_server, loser_new_nick)
  - Logic: Compare connection timestamps
  - If equal: use server ID hash
  - Return which server keeps the nick, what the loser becomes

### Part D: Configuration & Security

**Updates to `.env`:**
```env
CSC_SERVER_HOSTNAME=facingaddictionwithhope.com
CSC_SERVER_ID=server_001  # Unique ID for this server (for tie-breaking)
CSC_SERVER_LINK_PASSWORD=<secure_password>  # S2S link authentication
CSC_S2S_PORT=9526  # Port for server-to-server links
```

**Updates to `packages/csc-server/pyproject.toml`:**
- No new dependencies (use existing socket/asyncio)

## Testing Strategy

1. **Unit Tests:** `tests/test_s2s_protocol.py`
   - Test SLINK handshake
   - Test message parsing (SYNCUSER, SYNCCHAN, etc.)
   - Test collision detection and resolution

2. **Integration Tests:** `tests/test_s2s_integration.py`
   - Start 2 CSC servers on different ports
   - Link them together
   - Join user on server A, verify visible on server B
   - Send message from A to B, verify routing
   - Force nick collision, verify resolution

3. **Network Tests:** `tests/test_s2s_network.py`
   - 3+ servers in chain: A ↔ B ↔ C
   - Verify full-mesh or partial-mesh topology
   - Verify nick uniqueness across entire network

## Deliverables

1. **Core Protocol:**
   - [ ] `ServerLink` class (connect, auth, send/recv)
   - [ ] `ServerNetwork` class (manage multiple links)
   - [ ] S2S message handling in server_message_handler.py

2. **Collision Resolution:**
   - [ ] Collision detection logic
   - [ ] Nick rename algorithm
   - [ ] KICK message to user on rename

3. **Synchronization:**
   - [ ] User sync across servers
   - [ ] Channel sync across servers
   - [ ] Message routing between servers

4. **Configuration:**
   - [ ] .env variables for S2S
   - [ ] Server ID assignment
   - [ ] S2S port configuration

5. **Testing:**
   - [ ] Unit tests for S2S protocol
   - [ ] Integration tests for 2-server linking
   - [ ] Network tests for 3+ servers

## Notes

- **Do NOT break existing single-server IRC functionality** - S2S should be fully backward compatible
- **Thread safety critical** — Server link management must be thread-safe (use locks)
- **Message ordering** — S2S messages must preserve order (use TCP, not UDP)
- **Graceful degradation** — If a server link fails, remaining network continues operating
- **No circular links** — Prevent A→B→C→A loops (track already-visited servers)

## Success Criteria

- [x] Two or more CSC servers can link successfully
- [x] Users from different servers see each other in shared channels
- [x] Messages route correctly between servers
- [x] Nick collisions are detected and resolved automatically
- [x] Existing IRC clients and services still work normally
- [x] Server links survive client disconnects
- [x] Network continues operating if one link fails

## Commits Expected

```
[s2s-protocol] Implement ServerLink and ServerNetwork classes
[s2s-handlers] Add S2S command handlers to server_message_handler
[s2s-collision] Implement nick collision detection and resolution
[s2s-sync] Add user and channel synchronization across servers
[s2s-tests] Add comprehensive S2S linking tests
[s2s-config] Update .env and config for server linking
[s2s-docs] Document server federation architecture
```

## References

- RFC 2813 — Internet Relay Chat: Server-to-Server Protocol
- Current: `/opt/csc/packages/csc-server/server.py` (main server)
- Current: `/opt/csc/packages/csc-server/server_message_handler.py` (message handling)
--- RESTART Thu, Feb 19, 2026  1:41:35 PM ---
AGENT_PID: 1004
Reading prompt and planning implementation
Reading server.py and server_message_handler.py for integration points
Creating server_s2s.py with ServerLink and ServerNetwork classes
Reading WIP file and resuming server linking federation work
Reading server.py for integration points (init, run, broadcast methods)
Reading network.py and shared irc.py for protocol integration
Reading _dispatch_irc_command in server_message_handler.py for routing pattern
Creating server_s2s.py with ServerLink and ServerNetwork classes
Creating collision_resolver.py for nick collision resolution
Extending server.py with S2S network initialization and shutdown
Extending server_message_handler.py with S2S message routing for PRIVMSG, JOIN, PART, QUIT, NICK
- - -   R E S T A R T   T h u ,   F e b   1 9 ,   2 0 2 6     ( G e m i n i )   - - -  
 A G E N T _ P I D :   2 1 6 8 8  
 M o d i f y   s e r v e r _ s 2 s . p y :   A d d   s y n c _ n i c k _ c h a n g e ,   s y n c _ u s e r _ p a r t ,   a n d   h a n d l e   S Y N P A R T / S Y N C N I C K  
 M o d i f y   s e r v e r _ m e s s a g e _ h a n d l e r . p y :   A d d   S 2 S   h o o k s   f o r   N I C K   a n d   Q U I T ,   u p d a t e   P A R T   t o   u s e   S Y N P A R T  
 A d d   S Y N C L I N E   c o m m a n d   t o   S 2 S   f o r   g e n e r a l   I R C   l i n e   r o u t i n g  
 A d d   s y n c _ c h a n n e l _ s t a t e   h e l p e r   t o   S e r v e r N e t w o r k  
 A d d   S Y N C T O P I C   c o m m a n d   t o   S 2 S  
 A d d   C O N N E C T   I R C   c o m m a n d   f o r   o p e r a t o r s   t o   i n i t i a t e   S 2 S   l i n k s  
 A d d   S Q U I T   I R C   c o m m a n d   f o r   o p e r a t o r s   t o   d r o p   S 2 S   l i n k s  
 A d d   s t a r t u p _ t i m e   t r a c k i n g   t o   S e r v e r   f o r   t i m e   s y n c h r o n i z a t i o n  
 U p d a t e   c s c - c l i e n t / c l i e n t . p y :   A l l o w   h o s t / p o r t   o v e r r i d e s   i n   _ _ i n i t _ _   a n d   u s e   . e n v   v a l u e s  
 U p d a t e   c s c - c l a u d e / c l a u d e . p y :   P a s s   h o s t / p o r t   t o   s u p e r ( ) . _ _ i n i t _ _   a n d   u s e   . e n v   d e f a u l t s  
 U p d a t e   c s c - g e m i n i / g e m i n i . p y :   P a s s   h o s t / p o r t   t o   s u p e r ( ) . _ _ i n i t _ _   a n d   u s e   . e n v   d e f a u l t s  
 U p d a t e   c s c - c h a t g p t / c h a t g p t . p y :   P a s s   h o s t / p o r t   t o   s u p e r ( ) . _ _ i n i t _ _   a n d   u s e   . e n v   d e f a u l t s  
 U p d a t e   c s c - d o c k e r / d o c k e r _ c l i e n t . p y :   P a s s   h o s t / p o r t   t o   s u p e r ( ) . _ _ i n i t _ _   a n d   u s e   . e n v   d e f a u l t s  
 C r e a t e   t e s t s / t e s t _ s 2 s _ f e d e r a t i o n . p y   t o   v e r i f y   i m p l e m e n t a t i o n  
 U p d a t e   c o l l i s i o n _ r e s o l v e r . p y   t o   u s e   l e x i c o g r a p h i c a l   t i e b r e a k e r   f o r   s e r v e r   I D s  
 R e m o v e   d e b u g   l o g g i n g   f r o m   s e r v e r _ s 2 s . p y   a n d   c l e a n u p   t e s t s  
 