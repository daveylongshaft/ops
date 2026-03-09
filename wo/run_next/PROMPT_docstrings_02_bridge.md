# Prompt: Docstrings — Bridge Package

## Goal

Add full docstrings to all undocumented and minimally documented functions/methods in `/opt/csc/packages/csc-bridge/`. The bridge is the most complex underdocumented package — it has many one-liner docstrings that need expansion.

## Docstring Standard

**The bar: a developer must be able to call any function correctly by reading ONLY its docstring, without ever looking at the implementation.** If the docstring doesn't give you enough to call it right on the first try, it's incomplete.

**Why:** These docstrings are interface contracts, not implementation notes. Any function should be re-implementable in any language or logic model and the system still works — as long as the contract is honored. Document the *what*, not the *how*. The inputs, outputs, data shapes, error behavior, and side effects define the function. The code inside is just one way to satisfy that contract.

**Logic tables:** If a function's behavior can be fully described as a finite input→output mapping (e.g. command name → handler, numeric code → string, mode char → permission), document that mapping exhaustively in the docstring. This lets an implementer replace the logic with a simple lookup table/dict instead of branching code. List every valid input and its corresponding output.

Every docstring MUST include:

1. **Args** — every argument: name, type, valid values/ranges, constraints.
2. **Returns** — exact return type. Document every possible return value including None, empty collections, sentinel values. If it returns a dict, document the keys and value types.
3. **Raises** — every exception and under what conditions. If it silently swallows errors, say that.
4. **Data** — what data structures (self.*, globals, files, JSON) it reads, writes, or mutates. Include the shape (e.g. `dict[str, dict]` keyed by X, values are Y).
5. **Side effects** — network I/O, logging, broadcasting, disk writes, spawning threads.
6. **Thread safety** — locks used, shared state touched, concurrent access notes.
7. **Children** — non-trivial functions/methods this calls.
8. **Parents** — what calls this, if known and relevant.

```python
def _forward_to_server(self, session, line):
    """
    Forward a normalized IRC line from a bridge client to the upstream server.

    Args:
        session (BridgeSession): Active session. Must have server_sock connected
            and nick set. See session.py for BridgeSession fields.
        line (str): Raw IRC line from the client, without trailing CRLF.
            Will be normalized before forwarding.

    Returns:
        None

    Raises:
        OSError: If the server socket is disconnected. Caller should
            catch and call _destroy_session().

    Data:
        Reads session.server_sock (socket.socket), session.nick (str).
        Does not mutate session state.

    Side effects:
        Sends bytes over session.server_sock to the upstream CSC server.
        Logs the forwarded line at DEBUG level.

    Children:
        self.normalizer.normalize_client_to_server(line, session.nick)
        session.server_sock.sendall()

    Parents:
        Called by _client_listener() on each line received from the bridge client.
    """
```

**Omit sections only if truly not applicable.** When in doubt, include it.

## Files to Document

The analyzer doesn't flag these (they have bare one-liners), but they need full expansion:

### csc-bridge/data_bridge.py
- `BridgeData.__init__`, `create_user`, `validate_user`
- `add_history`, `set_favorite`, `get_favorite`, `get_favorites`, `_hash_password`

### csc-bridge/irc_normalizer.py
- `__init__`, `normalize_client_to_server`, `_normalize_client_line`
- `normalize_server_to_client`, `_normalize_server_line`
- `_send_notice`, `_send_numeric`

### csc-bridge/control_handler.py
- `__init__`, `handle_line`, `_handle_command`, `_try_auth`, `_send_welcome`

### csc-bridge/bridge.py
- `_destroy_session`, `_sniff_nick`, `_forward_to_server`
- `_handle_control_command`, `_forward_to_client`
- `_server_listener`, `_keepalive_loop`

### csc-bridge/irc.py and irc_utils.py
- `IRCMessage`, `parse_irc_message`, `format_irc_message`, `numeric_reply`

### csc-bridge/main.py
- Module docstring and `main()` function

## Already Well-Documented (skip these)
- `session.py`
- `transports/` (all files: tcp_inbound, tcp_outbound, udp_inbound, udp_outbound, base)

## Rules

- Do NOT change any code logic — docstrings only
- Read each file before editing
- Use Haiku-tier agents for bulk work

## Work Log

### Session 1 (START)
- [X] Read task requirements, move to wip/
- [X] Add docstrings to bridge.py + main.py (agent)
- [X] Add docstrings to data_bridge.py, irc_normalizer.py, control_handler.py (agent)
- [X] Add docstrings to irc.py, irc_utils.py (agent)
- [X] Fix 5 remaining short docstrings (get_history, _send_numeric, send_notice, _send_raw, Network class)
- [X] Verify 0 short/missing docstrings in csc-bridge (excluding build/ and transports/)
- [X] TASK COMPLETE

Verified complete.
