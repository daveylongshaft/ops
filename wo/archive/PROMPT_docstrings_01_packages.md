# Prompt: Docstrings — Package Source Files

## Goal

Add full docstrings to all undocumented functions/methods in the package source code under `/opt/csc/packages/`. This is the core codebase — these docstrings feed directly into the `tools/` code maps that developers read before touching source files.

## Docstring Standard

**The bar: a developer must be able to call any function correctly by reading ONLY its docstring, without ever looking at the implementation.** If the docstring doesn't give you enough to call it right on the first try, it's incomplete.

**Why:** These docstrings are interface contracts, not implementation notes. Any function should be re-implementable in any language or logic model and the system still works — as long as the contract is honored. Document the *what*, not the *how*. The inputs, outputs, data shapes, error behavior, and side effects define the function. The code inside is just one way to satisfy that contract.

**Logic tables:** If a function's behavior can be fully described as a finite input→output mapping (e.g. command name → handler, numeric code → string, mode char → permission), document that mapping exhaustively in the docstring. This lets an implementer replace the logic with a simple lookup table/dict instead of branching code. List every valid input and its corresponding output.

Every docstring MUST include:

1. **Args** — every argument: name, type, valid values/ranges, constraints. If a string must be non-empty or lowercase, say so. If a dict must have specific keys, list them.
2. **Returns** — exact return type. Document every possible return value including None, empty collections, sentinel values. If it returns a dict, document the keys and value types. If it returns a tuple, document each position.
3. **Raises** — every exception this function can raise and under what conditions. If it silently swallows errors, say that too.
4. **Data** — what data structures (self.*, globals, files on disk, JSON) it reads, writes, or mutates. Include the shape: `self.members` is `dict[str, dict]` keyed by lowercase nick, values are `{"nick": str, "modes": set[str], "op": bool}`. If it writes to disk, say what file and format.
5. **Side effects** — network I/O, logging, broadcasting to clients, disk writes, spawning threads. Anything that happens beyond computing a return value.
6. **Thread safety** — if the function uses locks, is called from multiple threads, or touches shared state, say so.
7. **Children** — non-trivial functions/methods this calls (skip builtins like len/str).
8. **Parents** — what calls this, if known and relevant.

```python
def add_member(self, nick, modes=None):
    """
    Add a user to this channel's member list.

    Args:
        nick (str): Display nick of the user (e.g. "Alice"). Stored as-is
            for display, but keyed internally by nick.lower().
        modes (set[str] | None, optional): Initial mode flags (e.g. {"o", "v"}).
            Defaults to empty set if None.

    Returns:
        None

    Raises:
        No exceptions. If nick is already a member, overwrites the entry silently.

    Data:
        Mutates self.members (dict[str, dict]). Adds key nick.lower() with value:
            {"nick": str (display case), "modes": set[str], "op": bool}
        Increments self._member_count.

    Side effects:
        None. Does not persist to disk — caller is responsible for saving.

    Thread safety:
        Not thread-safe. Caller must hold channel lock if accessed concurrently.

    Children:
        None.

    Parents:
        Called by Server._handle_join(), _handle_names() during channel sync.
    """
```

For simple properties, still cover return type and data source:
```python
@property
def member_count(self):
    """Return number of members in this channel.

    Returns:
        int: Count of entries in self.members dict.

    Data:
        Reads self.members (dict[str, dict]). No mutation.
    """
```

**Omit sections only if truly not applicable** (e.g. a pure function with no side effects can skip "Side effects" and "Thread safety"). When in doubt, include it.

## Files and Items to Document

### csc-shared/channel.py (3 items)
- `Channel.__init__` (line 24)
- `Channel.member_count` property (line 76)
- `ChannelManager.__init__` (line 121)

### csc-client/client_file_handler.py (2 items)
- `ClientFileHandler.__init__` (line 10)
- `ClientFileHandler.has_active_session` (line 17)

### csc-client/client_service_handler.py (2 items)
- `ClientServiceHandler.__init__` (line 13)
- `ClientServiceHandler.get_help` (line 112)

### csc-chatgpt/chatgpt.py (1 item)
- `ChatGPT._input_handler` (line 413)

### csc-chatgpt/main.py (1 item)
- `main()` (line 11)

### csc-claude/claude.py (1 item)
- `Claude._input_handler` (line 668)

### csc-gemini/main.py (1 item)
- `main()` (line 11)

**Total: 11 items**

## Also Expand These Minimal One-Liners

The analyzer won't flag these because they technically have docstrings, but they're bare one-liners that need the full convention. **Read each file first** to understand the code, then expand:

### csc-shared/channel.py
- `add_member`, `remove_member`, `has_member`, `get_member`, `get_display_nick`
- `is_op`, `has_voice`, `can_speak`, `can_set_topic`
- `ChannelManager.ensure_channel`, `get_channel`, `remove_channel`, `list_channels`
- `find_channels_for_nick`, `remove_nick_from_all`

### csc-shared/irc.py
- `IRCMessage` class, `parse_irc_message`, `format_irc_message`, `numeric_reply`

### csc-shared/chat_buffer.py
- `ChatBuffer.__init__`, `_get_lock`

### csc-shared modules (module-level docstrings)
- `log.py`, `data.py`, `version.py`, `secret.py`, `network.py` — all missing module docstrings

### csc-client/main.py, csc-server/main.py, csc-server/service.py, csc-bridge/main.py, csc-claude/main.py
- Missing module and/or `main()` docstrings

## Rules

- Do NOT change any code logic — docstrings only
- Read each file before editing (use Read tool, then Edit tool)
- Use Haiku-tier agents for bulk work
- After finishing, run: `python3 /opt/csc/analyze_project.py` to verify the package items drop to zero

## Work Log

### Session 1 (START)
- [X] Read task requirements
- [X] Move to wip/
- [X] Add docstrings to csc-shared/channel.py
- [X] Add docstrings to csc-shared/irc.py + other shared modules
- [X] Add docstrings to client, AI clients, server, bridge
- [X] Verify all agents complete successfully
- [X] Run analyze_project.py — 0 undocumented in source packages (9 in stale build/lib/ artifacts only)
- [X] TASK COMPLETE

Verified complete.
