# PROMPT 100: Bot Log Monitoring and Echoing

**Agent:** claude sonnet
**Goal:** Implement functionality for registered bots to monitor specified system logs and echo new entries to their respective channels. This allows AI agents to monitor and react to system events in real-time.

## Context

This prompt assumes that BOTSERV (PROMPT 99) is implemented and channels can have registered bots. The goal is to extend bot capabilities to include real-time log monitoring and reporting. This feature is crucial for AI agents (like Gemini) to observe server events, errors, or specific activities without direct file system access, enabling them to react and assist proactively.

## Requirements

### 1. Extend BOTSERV Service (`services/botserv_service.py`)
- **Bot Configuration:** Extend the bot registration data (e.g., in `botserv.db`) to include:
    - A list of log files to monitor for each registered bot (e.g., `/opt/csc/logs/Server.log`, `/opt/csc/logs/Gemini.log`).
    - A flag or setting to enable/disable log monitoring for a bot.
- **Command: `SETLOG <botnick> <#channel> <log_file> [enable/disable]`:**
    - **Authorization:** Only the channel owner or an IRC operator.
    - Set or clear a log file for a specific bot to monitor.
    - Example: `MSG BOTSERV SETLOG mybot #general /opt/csc/logs/Server.log enable`
- **Internal Log Monitor:**
    - Implement a mechanism within `botserv_service.py` (e.g., a dedicated thread or a periodic check) that actively monitors the specified log files for *new* entries for each enabled bot.
    - This mechanism should efficiently read only new lines appended to the log files since the last check. Consider using file pointers or tracking file sizes.
    - It should handle multiple bots monitoring different log files simultaneously without conflicts.

### 2. Log Echoing to Channel
- **Message Format:** When new log entries are detected:
    - The registered bot should send a `PRIVMSG` to its associated channel.
    - The message content should be the new log line, potentially prefixed with the log filename for clarity (e.g., `[Server.log] <new log line>`).
    - Ensure messages are correctly formatted for IRC (e.g., respecting message length limits and splitting if necessary).
- **Rate Limiting/Filtering:** Implement basic rate limiting (e.g., no more than X messages per second per bot) and/or simple filtering (e.g., ignore lines matching certain regex patterns) to prevent log flooding.

### 3. Server Integration
- **BOTSERV Presence:** The `BOTSERV` server-side user should also be able to "send" messages as the registered bot nicks. This might require updating `server.py` or `server_message_handler.py` to allow `BOTSERV` to impersonate a bot nick for `PRIVMSG` when echoing logs. (Perhaps by having `botserv_service` call a server method that broadcasts a message from a given bot nick).

### 4. AI Reaction (Information only, no implementation in this prompt)
- The echoed log messages provide a real-time feed for AI clients (like Gemini, Claude) to monitor system health, detect errors, or observe specific events, allowing them to proactively respond or take action via other service commands.

## Deliverables
- Updates to `/opt/csc/services/botserv_service.py` (new commands, log monitoring logic, echoing).
- Updates to `/opt/csc/packages/csc_server/server_message_handler.py` and/or `/opt/csc/packages/csc_server/server.py` to enable bot-nick `PRIVMSG` from `BOTSERV` and integrate log monitoring calls.
- `botserv.db` schema updates.
- Potential new log files or configuration if needed for monitoring (e.g., `botserv_monitor.log`).

## Work Log (to be updated by agent)

echo "Creating prompt file 100_bot_log_monitoring.md" >> /opt/csc/prompts/wip/100_bot_log_monitoring.md
AGENT_PID: 291749 AGENT_NAME: claude sonnet
assigning 100_bot_log_monitoring.md to claude sonnet
--- RESTART Tue 17 Feb 2026 08:43:24 PM GMT ---
AGENT_PID: 299530
