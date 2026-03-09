# Prompt: Convert Eligible Functions to Lookup Tables

## Background

An audit of `/opt/csc/packages/` and `/opt/csc/services/` identified functions whose logic can be fully expressed as finite input→output mappings. These should be converted from if/elif chains to dict lookups for clarity, performance, and to make the logic table explicit and portable.

## Why This Matters

A dict lookup is:
- **Faster** — O(1) hash vs sequential branch evaluation
- **Readable** — the entire truth table is visible in one place
- **Portable** — any language or logic model can implement a lookup table
- **Testable** — you can iterate the dict to verify every case

---

## CONVERT THESE (Strong Candidates)

### 1. User Mode Handlers
**File:** `packages/csc-server/server_message_handler.py` lines 1128-1172
**Current:** if/elif chain mapping mode chars (+o, +a, +i, +w, +s) to behavior
**Convert to:**
```python
# Mode char → handler function
USER_MODE_HANDLERS = {
    "i": self._apply_simple_mode,    # invisible
    "w": self._apply_simple_mode,    # wallops
    "s": self._apply_simple_mode,    # server notices
    "o": self._apply_oper_mode,      # operator (special perms)
    "a": lambda *_: None,            # away (set via AWAY cmd, ignore here)
}
```
**Entries:** 5
**Saves:** ~30 lines of branching → 5-line dict + small handler functions

### 2. Bridge Control Handler /trans Commands
**File:** `packages/csc-bridge/control_handler.py` lines 140-173
**Current:** if/elif chain dispatching subcommands
**Convert to:** dict mapping subcommand → handler function
**Entries:** 4-6 subcommands

### 3. IRC Normalizer Command Filters
**File:** `packages/csc-bridge/irc_normalizer.py` line 96
**Current:** `if command in ("ISOP", "BUFFER", "AI")` + separate CRYPTOINIT check
**Convert to:**
```python
# Commands to filter out with their action
CSC_ONLY_COMMANDS = {
    "ISOP": "unsupported",
    "BUFFER": "unsupported",
    "AI": "unsupported",
    "CRYPTOINIT": "drop_silent",
}
```
**Entries:** 4

### 4. CAP Subcommand Dispatch
**File:** `packages/csc-bridge/irc_normalizer.py` lines 126-137
**Current:** if/elif chain for CAP LS/LIST/REQ/END
**Convert to:** dict mapping subcmd → response action
**Entries:** 4

### 5. Bridge Protocol/Dialect Selection
**File:** `packages/csc-bridge/bridge.py` (connection setup)
**Current:** if/elif for protocol (tcp/udp) × dialect (csc/rfc)
**Convert to:**
```python
TRANSPORTS = {
    "tcp": TCPTransport,
    "udp": UDPTransport,
}
DIALECTS = {
    "csc": CscNormalizer,
    "rfc": None,  # passthrough
}
```
**Entries:** 4

---

## ALREADY OPTIMIZED (No Changes Needed)

These are already dict/set lookups — document them as exemplary patterns:

| Location | What | Pattern |
|----------|------|---------|
| `server_message_handler.py:155-228` | IRC command dispatch | Two dicts: pre_reg_commands, post_reg_commands |
| `server_message_handler.py:1029-1035` | Channel mode classification | Four frozensets: _NICK_MODES, _FLAG_MODES, _PARAM_MODES, _LIST_MODES |

---

## NOT CANDIDATES (Rejected)

| Function | File | Reason |
|----------|------|--------|
| `parse_irc_message()` | csc-shared/irc.py | State machine string parser, unbounded input |
| `format_irc_message()` | csc-shared/irc.py | String builder with conditional formatting |
| `Channel.get_names_list()` | csc-shared/channel.py | Loop over members with prefix formatting |
| `Channel.can_speak()` | csc-shared/channel.py | Multi-condition permission check (AND/OR) |
| `_handle_channel_mode()` | server_message_handler.py | Complex state machine with side effects |
| `download_url_content()` | services/builtin_service.py | Network I/O |
| `read_file_content()` | services/builtin_service.py | File I/O |
| `list_dir()` | services/builtin_service.py | Filesystem, unbounded input |
| `backup.create()` | services/backup_service.py | Archive creation, side effects |
| `patch.apply()` | services/patch_service.py | Diff parsing, sequential processing |
| `curl.run()` | services/curl_service.py | HTTP client, side effects |
| `ntfy.send()` | services/ntfy_service.py | Service delegation, side effects |
| `prompts_manager.status()` | services/prompts_manager.py | Path-based checks, unbounded input |
| `module_manager._validate_service_file()` | services/module_manager_service.py | AST parsing, complex validation |

---

## Rules

- Do NOT change behavior — same inputs must produce same outputs
- Add the lookup dict as a class constant or module constant
- Keep the handler functions small — the dict IS the logic, handlers are just the actions
- Add docstrings to the new dicts documenting every entry (per the docstring standard)
- Run tests after each conversion: `python -m pytest tests/ -v`
- Use Haiku-tier agents for the straightforward conversions

---

## Work Log

### Session 1 (START)
- [X] Read source files for all 5 conversion targets
- [X] Convert #1: User Mode Handlers (server_message_handler.py) — ALREADY DONE (line 1129 dict lookup)
- [X] Convert #2: Bridge Control Handler /trans Commands (control_handler.py) — ALREADY DONE (line 284 dispatch table)
- [X] Convert #3: IRC Normalizer Command Filters (irc_normalizer.py) — ALREADY DONE (line 215 dict + CRYPTOINIT special case)
- [X] Convert #4: CAP Subcommand Dispatch (irc_normalizer.py) — ALREADY DONE (line 251 dict dispatch)
- [X] Convert #5: Bridge Protocol/Dialect Selection (bridge.py/control_handler.py) — ALREADY DONE (lines 347-360 two dicts)
- [X] Run tests to verify no behavior changes — N/A, all 5 targets were already dict lookups, zero code changes made

Verified complete — all conversions already implemented prior to this prompt.
