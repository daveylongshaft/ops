# PROMPT 98: Enhance ChanServ with Enforcement and Strict Modes

**Agent:** claude sonnet
**Goal:** Implement advanced ChanServ features for channel enforcement and strict operator/voice modes.

## Context

ChanServ core functionality (registration, basic OP/VOICE/BAN) is assumed to be implemented (see PROMPT 97). This prompt focuses on adding enforcement and strictness related to channel topics, operator status, and voice status, all managed by ChanServ.

## Requirements

### 1. Register Enforce Mode for Channels
- **New ChanServ Command/Mode:** Introduce a mechanism (e.g., a ChanServ command like `CHANSERV SET <#chan> ENFORCEMODE <on/off>` or a channel mode `+E`) that, when active, requires users to be registered with NickServ (and identified) to gain `+o` or `+v` status in the channel.
- **Integration with NickServ:** ChanServ must interact with NickServ (or the server's `nickserv_identified` state) to verify if a user is identified for their current nick.
- **Enforcement:** If a user is not identified and attempts to gain `+o` or `+v`, ChanServ should prevent it or immediately deop/devoice them.

### 2. Enforce Topics
- **Channel Mode for Topic Enforcement:** Introduce a channel mode (e.g., `+T`) that, when set on a registered channel, restricts topic changes.
- **Restriction:** If `+T` is active, only the channel owner (as registered in ChanServ) or an IRC operator can change the channel topic.
- **Enforcement:** If an unauthorized user attempts to change the topic on a `+T` channel, ChanServ should revert the topic to the last authorized one and send an error message to the user.

### 3. Optional Strict Ops and Voice
- **New Channel Modes:** Introduce separate channel modes for strict ops (e.g., `+S`) and strict voice (e.g., `+V`). These modes should be manageable via ChanServ (e.g., `CHANSERV SET <#chan> STRICTOPS <on/off>`).
- **Strict Ops (`+S`):**
    - If `+S` is active on a registered channel:
        - A user *must* be in ChanServ's oplist for that channel to receive or retain `+o` mode.
        - If a user not in ChanServ's oplist receives `+o` (e.g., from another ChanOp or IRC operator), ChanServ should immediately deop them (`-o`).
- **Strict Voice (`+V`):**
    - If `+V` is active on a registered channel:
        - A user *must* be in ChanServ's voicelist for that channel to receive or retain `+v` mode.
        - If a user not in ChanServ's voicelist receives `+v`, ChanServ should immediately devoice them (`-v`).
- **Interaction with `_handle_mode`:** ChanServ's enforcement logic should be called during `_handle_mode` processing in `server_message_handler.py` to intercept and correct mode changes.

## Deliverables
- Updates to `/opt/csc/services/chanserv_service.py` (new commands, enforcement logic).
- Updates to `/opt/csc/packages/csc_server/server_message_handler.py` (to integrate with new modes and enforcement).
- Updates to `chanserv.db` schema (to store new settings like `enforce_mode`, `enforce_topic`, `strict_ops`, `strict_voice`).
- Potential minor updates to `/opt/csc/packages/csc_server/server.py` if global settings or new attributes are needed.

## Work Log (to be updated by agent)

echo "Creating prompt file 98_enhance_chanserv_modes.md" >> /opt/csc/prompts/wip/98_enhance_chanserv_modes.md
AGENT_PID: 291617 AGENT_NAME: claude sonnet
assigning 98_enhance_chanserv_modes.md to claude sonnet
--- RESTART Tue 17 Feb 2026 08:37:08 PM GMT ---
AGENT_PID: 299530
