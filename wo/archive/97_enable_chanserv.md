# PROMPT 97: Enable and Complete ChanServ Service

**Agent:** claude sonnet
**Goal:** Fully enable and implement the core ChanServ functionality, integrating it with the IRC server.

## Context

The `chanserv_service.py` exists but is currently located in `services/disabled_services/`. The goal is to make it a fully functional service that manages channel registration, access control (ops, voice, bans), and topic enforcement as described below.

Data for registered channels should be stored persistently, ideally managed by `PersistentStorageManager` if suitable, or a new `chanserv.db` file. The existing `chanserv_service.py` is expected to manage a `chanserv.db` file.

## Requirements

### 1. Enable ChanServ Service
- Move `/opt/csc/services/disabled_services/todolist_service.py` to `/opt/csc/services/chanserv_service.py`. (Correction: it's actually `chanserv_service.py` not `todolist_service.py`)
- Update `/opt/csc/packages/csc_server/server_message_handler.py` to recognize `PRIVMSG ChanServ` commands and route them to `chanserv_service.py`. Ensure the routing correctly extracts the subcommand and arguments.

### 2. Implement Core ChanServ Commands (`services/chanserv_service.py`)
- **Data File:** Manage channel data in `chanserv.db` (or integrate with `PersistentStorageManager` if a better pattern exists).
- **`REGISTER <#chan> <topic>`:**
    - Only a channel operator (`+o`) or IRC operator (`oper`) can register a channel.
    - If successful, create a record for the channel in `chanserv.db`, including owner (the registering user), topic, and initial empty lists for ops, voice, and bans.
    - Send a success message to the user.
    - If registration fails (e.g., channel already registered, user not authorized), send an appropriate error message.
- **`OP <#chan> <nick>`:**
    - Only the channel owner or an IRC operator can use this command.
    - Add `<nick>` to the oplist for `<#chan>` in `chanserv.db`.
    - Grant `+o` mode to `<nick>` in the channel.
    - If `nick` is not in the channel, add them to oplist but do not grant mode.
    - Send a success or error message.
- **`VOICE <#chan> <nick>`:**
    - Only the channel owner or an IRC operator can use this command.
    - Add `<nick>` to the voicelist for `<#chan>` in `chanserv.db`.
    - Grant `+v` mode to `<nick>` in the channel.
    - If `nick` is not in the channel, add them to voicelist but do not grant mode.
    - Send a success or error message.
- **`BAN <#chan> <mask?>`:**
    - Only the channel owner or an IRC operator can use this command.
    - Add `<mask>` to the banlist for `<#chan>` in `chanserv.db`.
    - Enforce the ban by kicking any currently joined users matching the mask and preventing new joins.
    - If no `mask` is provided, list existing bans for the channel.
    - Send a success or error message.
- **`DEOP <#chan> <nick>` / `DEVOICE <#chan> <nick>` / `UNBAN <#chan> <mask>`:** Implement corresponding commands to remove ops, voice, and bans.

### 3. Internal `apply_channel_state(channel)` (within ChanServ service)
- This internal method should be callable by the server.
- When called, it should:
    - Set the channel topic based on `chanserv.db` (if registered).
    - Apply channel modes (e.g., `+t` for topic enforcement, `+m` for moderated).
    - Apply user modes (`+o`, `+v`) to users currently in the channel based on `chanserv.db` lists.
    - Enforce bans: Kick any users matching the banlist.

### 4. Server Integration (`packages/csc_server/server_message_handler.py`)
- **`_handle_join`:**
    - When a user attempts to `JOIN` a channel:
        - If the channel is registered with ChanServ:
            - Check `banlist` in `chanserv.db`: If the user is banned, reject `JOIN` with `ERR_BANNEDFROMCHAN`.
            - Check `oplist` in `chanserv.db`: If the user is in the oplist, automatically grant `+o` mode upon successful join.
            - Check `voicelist` in `chanserv.db`: If the user is in the voicelist, automatically grant `+v` mode upon successful join.
        - Preserve existing logic for new channels (first user gets `+o`).
- **`_handle_mode`:** If a channel is registered with ChanServ, ensure that ChanServ's stored modes/user lists are respected and potentially used to override client-issued modes if they conflict with ChanServ's management.
- **Call `apply_channel_state`:** Integrate calls to `chanserv_service.py.apply_channel_state` during relevant events (e.g., after `JOIN`, `PART`, `MODE` changes, and on server startup/restore).

## Deliverables
- `/opt/csc/services/chanserv_service.py` (new/moved and implemented)
- Updates to `/opt/csc/packages/csc_server/server_message_handler.py`
- Updates to `/opt/csc/packages/csc_server/server.py` (to integrate PersistentStorageManager or load `chanserv.db`)
- `chanserv.db` (new file, managed by ChanServ)

## Work Log (to be updated by agent)

echo "Creating prompt file 97_enable_chanserv.md" >> /opt/csc/prompts/wip/97_enable_chanserv.md
AGENT_PID: 291577 AGENT_NAME: claude sonnet
assigning 97_enable_chanserv.md to claude sonnet
Renaming directory /opt/csc/packages/csc_server to /opt/csc/packages/csc-server to resolve path mismatch.
Moving all service files from /opt/csc/services/ to /opt/csc/packages/csc_shared/services/ and creating __init__.py.
Adding _handle_service_via_chatline method to MessageHandler in packages/csc-server/server_message_handler.py to process AI commands.
Adding debug log to _dispatch_irc_command in packages/csc-server/server_message_handler.py to inspect parsed command and registration status.
--- RESTART Tue 17 Feb 2026 08:27:44 PM GMT ---
AGENT_PID: 299530
