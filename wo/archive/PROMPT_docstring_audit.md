# Prompt: Add Missing and Incomplete Docstrings Across All Packages

## Problem Statement

An audit of `/opt/csc/packages/` revealed 78 undocumented functions/methods and many more with minimal one-liner docstrings that lack parameter details, return values, and usage context. This hurts developer onboarding and AI-assisted development.

## Scope

All Python files in `/opt/csc/packages/`. Every module, class, method, function, and property should have a full docstring following the project's existing convention:

```
- What it does: ...
- Arguments: ...
- What calls it: ...
- What it calls: ...
- Returns: ...
```

## Files Needing Work

### Critical — Missing docstrings entirely:
- `csc-shared/log.py` — missing module docstring
- `csc-shared/data.py` — missing module docstring; `store_data()` and `run()` are sparse
- `csc-shared/version.py` — missing module docstring
- `csc-shared/secret.py` — missing module docstring; most getter functions are one-liners
- `csc-shared/network.py` — missing module docstring; `connected_for()` is minimal
- `csc-bridge/main.py` — missing module and `main()` docstrings
- `csc-server/main.py` — missing module and `main()` docstrings
- `csc-server/service.py` — missing module docstring
- `csc-client/main.py` — missing module and `main()` docstrings
- `csc-claude/main.py` — missing module and `main()` docstrings

### High Priority — Minimal one-liner docstrings:
- `csc-shared/channel.py` — almost every method is a bare one-liner: `add_member`, `remove_member`, `has_member`, `get_member`, `get_display_nick`, `is_op`, `has_voice`, `can_speak`, `can_set_topic`, `ChannelManager.__init__`, `ensure_channel`, `get_channel`, `remove_channel`, `list_channels`, `find_channels_for_nick`, `remove_nick_from_all`
- `csc-shared/irc.py` — `IRCMessage`, `parse_irc_message`, `format_irc_message`, `numeric_reply` all minimal
- `csc-shared/chat_buffer.py` — `ChatBuffer.__init__()` and `_get_lock()` need expansion
- `csc-bridge/data_bridge.py` — `BridgeData.__init__`, `create_user`, `validate_user`, `add_history`, `set_favorite`, `get_favorite`, `get_favorites`, `_hash_password`
- `csc-bridge/irc_normalizer.py` — `__init__`, `normalize_client_to_server`, `_normalize_client_line`, `normalize_server_to_client`, `_normalize_server_line`, `_send_notice`, `_send_numeric`
- `csc-bridge/control_handler.py` — `__init__`, `handle_line`, `_handle_command`, `_try_auth`, `_send_welcome`
- `csc-bridge/bridge.py` — `_destroy_session`, `_sniff_nick`, `_forward_to_server`, `_handle_control_command`, `_forward_to_client`, `_server_listener`, `_keepalive_loop`
- `csc-bridge/irc.py` and `irc_utils.py` — `IRCMessage`, `parse_irc_message`, `format_irc_message`, `numeric_reply`

### Already Well-Documented (no changes needed):
- `csc-shared/root.py`
- `csc-shared/crypto.py`
- `csc-bridge/session.py`
- `csc-bridge/transports/` (all files: tcp_inbound, tcp_outbound, udp_inbound, udp_outbound, base)
- `csc-server/server.py` (most methods)
- `csc-server/server_message_handler.py` (most methods)

## Deliverables

- All files listed above updated with full docstrings
- Run `python3 /opt/csc/analyze_project.py` after changes to regenerate `tools/` and verify zero undocumented items in `analysis_report.json`

## Notes

- Do NOT change any code logic — docstrings only
- Follow the existing docstring convention used in `server.py` and `server_message_handler.py`
- Use Haiku-tier agents for the bulk of the work (straightforward edits)

Verified complete.
