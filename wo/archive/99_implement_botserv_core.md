# PROMPT 99: Implement Core BOTSERV and Bot Registration

**Agent:** claude sonnet
**Goal:** Create the BOTSERV server-side user, implement its command interception, and enable channel bot registration.

## Context

This prompt follows the implementation of ChanServ (PROMPT 97 and 98). BOTSERV will be a core server service, not a regular client. It will manage the registration of other "bot" nicks to channels, allowing channel owners to delegate certain management tasks or monitoring functions to these bots.

## Requirements

### 1. Create BOTSERV Server-Side User
- **Server Representation:** Introduce a special server-side "user" named `BOTSERV`. This user should be handled by the server directly, not as a regular connected client.
- **No Network Interaction:** `BOTSERV` should not have an associated network address, should not respond to PING/PONG, and should not timeout. It exists purely as a logical entity within the server to receive commands.
- **Service Name:** The associated service will be `botserv_service.py`.

### 2. Implement Core BOTSERV Service (`services/botserv_service.py`)
- Create a new file `/opt/csc/services/botserv_service.py`.
- **Data File:** Manage registered bots persistently, for example, in a `botserv.db` file or by extending `PersistentStorageManager`. The data should link a channel, a bot's nickname, and potentially an owner/password.
    - Format: `<channel>:<botnick>:<owner_nick>:<password_hash>:<registered_at>`
- **Command: `ADD <botnick> <#channel> <password>`:**
    - **Authorization:** Only the registered *owner* of `<#channel>` (as determined by ChanServ) or an IRC operator can register a bot for that channel.
    - **Validation:**
        - `botnick` must be a valid IRC nickname and not already in use.
        - `#channel` must be a registered channel (interact with ChanServ).
        - `password` for the bot.
    - **Registration:** If valid, register the `<botnick>` for `<#channel>` with the specified `<password>` and the registering user as the owner.
    - Send success or error messages (e.g., `NOTICE` from `BOTSERV`).
- **Command: `DEL <botnick> <#channel>`:**
    - **Authorization:** Only the channel owner or an IRC operator.
    - Deregister the specified bot from the channel.
- **Command: `LIST [channel]`:**
    - List all registered bots or bots for a specific channel.

### 3. Server Integration (`packages/csc_server/server_message_handler.py`)
- **Intercept `PRIVMSG BOTSERV` and `NOTICE BOTSERV`:** Modify `_dispatch_irc_command` to:
    - Detect incoming `PRIVMSG` or `NOTICE` messages where the target is `BOTSERV` (case-insensitive).
    - Extract the subcommand and arguments from the message.
    - Route these commands to `botserv_service.py`'s `handle_command` or specific methods.
    - Ensure `BOTSERV` commands are processed as server-side actions, not as messages to a regular client.

## Deliverables
- `/opt/csc/services/botserv_service.py` (new and implemented)
- Updates to `/opt/csc/packages/csc_server/server_message_handler.py` (command routing)
- Updates to `/opt/csc/packages/csc_server/server.py` (to define `BOTSERV` as a special internal user and potentially manage `botserv.db` via `PersistentStorageManager`).
- `botserv.db` (new file, managed by BOTSERV)

## Work Log (to be updated by agent)

echo "Creating prompt file 99_implement_botserv_core.md" >> /opt/csc/prompts/wip/99_implement_botserv_core.md
AGENT_PID: 291720 AGENT_NAME: claude sonnet
assigning 99_implement_botserv_core.md to claude sonnet
--- RESTART Tue 17 Feb 2026 08:40:00 PM GMT ---
AGENT_PID: 299530
