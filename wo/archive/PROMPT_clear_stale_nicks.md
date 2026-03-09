# Prompt: Proactively Clear Stale Nicks from Server

## Problem Statement

Currently, the server might retain "stale" nicks in its `onlineresume` or equivalent client tracking mechanisms. These are nicks associated with clients that have timed out due to ping-pong failures or other disconnects, but are not being proactively removed from active client lists. This can lead to:

- Inaccurate `WHOIS` or `NAMES` responses.
- Resource consumption for non-existent connections.
- Potential issues with nick collisions if a new user tries to claim a "stale" nick.

## Desired Behavior

The CSC server should proactively identify and clear stale nicks from its `onlineresume` (or any equivalent structure storing active client information) when a client connection times out due to ping-pong failures or other disconnects. This ensures that only genuinely active clients are tracked.

## Implementation Details

1.  **Investigation:**
    *   Examine `/opt/csc/packages/csc-server/` to understand how client connections are managed, especially focusing on ping-pong mechanisms, timeout detection, and the `onlineresume` (or similar) data structure.
    *   Identify the code paths responsible for client disconnection and cleanup.

2.  **Modification:**
    *   Implement logic to ensure that when a client connection is determined to be stale (e.g., via ping-pong timeout), its associated nick is immediately and thoroughly removed from all relevant server-side active client tracking structures, including `onlineresume`.
    *   Ensure that any associated resources (e.g., user objects, channel memberships for that user) are also cleaned up appropriately.

3.  **Verification:**
    *   Add or update unit/integration tests in `/opt/csc/tests/` to confirm that stale nicks are correctly removed after a simulated timeout.
    *   Verify that `WHOIS` queries for removed nicks return appropriate "no such nick" responses.

## Deliverables

-   Modified server-side code in `csc-server` to proactively clear stale nicks.
-   Updated or new tests demonstrating the correct functionality.
-   Documentation updates (if necessary) in `/opt/csc/docs/server.md` to reflect the new timeout handling and cleanup process.

## Work Log

### Session 1 (START + COMPLETE)
- [X] Investigate `csc-server` for client management, ping-pong, timeouts, and `onlineresume`.
- [X] Identify code paths for client disconnection and cleanup.
- [X] Develop a plan for implementing proactive stale nick removal.
- [X] Implement changes:
  - **server.py `_run_cleanup_once()`** — replaced manual cleanup with `_server_kill(nick, "Ping timeout")` so timed-out clients get full disconnect: QUIT broadcast to channels, channel removal, registration cleanup, NickServ cleanup, WHOWAS history, and persist.
  - **server.py `broadcast()`** — removed inline `clients.pop()` for stale clients; now just skips them and lets the cleanup loop handle proper disconnect.
  - **storage.py `restore_users()`** — expired sessions now also call `remove_nick_from_all()` and `remove_user()` to clean stale nicks from channels and disk on startup.
- [X] Added `/opt/csc/tests/test_stale_nick_cleanup.py` with 9 tests — all passing:
  - test_server_kill_removes_nick_from_clients
  - test_server_kill_removes_from_channels
  - test_server_kill_removes_registration_state
  - test_server_kill_removes_nickserv_identified
  - test_server_kill_broadcasts_quit
  - test_server_kill_persists_disconnection_history
  - test_server_kill_unknown_nick_returns_false
  - test_server_kill_frees_nick_for_reuse
  - test_stale_client_removed_from_multiple_channels

Verified complete.
