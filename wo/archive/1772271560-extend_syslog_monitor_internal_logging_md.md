# Extend Syslog Monitor - Internal Server Logging System

## Objective

Extend the existing `tools/syslog_monitor.py` pattern into a flexible internal server logging system that:
1. Reads multiple log files (pm-execution-journal, queue-worker log, test-runner logs, etc.)
2. Maps each file to one or more IRC channels
3. Posts new lines to channels as messages FROM reserved system nicks
4. Configurable via JSON - no code changes needed to add new log streams
5. Runs internal to the server (no IRC bot client setup needed)
6. Reserves nicks in nickserv (system-level nicks like "PM", "QueueWorker", "TestRunner")

## Current State

Existing `tools/syslog_monitor.py`:
- Reads `/var/log/syslog`
- Tracks file position (state file)
- Outputs new lines to stdout
- Polls periodically

**Goal:** Generalize to support:
- Any log file (not just syslog)
- Many-to-many file-to-channel mapping
- Direct channel writes (internal to server)
- Configurable via JSON

## Architecture

### 1. Extended Syslog Monitor (tools/log_monitor.py)

```python
#!/usr/bin/env python3
"""
Generic log file monitor with configurable file-to-channel mapping.
Polls log files, tracks positions, writes new lines to IRC channels.
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime

class LogMonitor:
    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        self.state_dir = Path(self.config.get("state_dir", "/opt/csc/tools/log_monitor_state"))
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self, config_file):
        """Load log-to-channel mapping from JSON config."""
        with open(config_file, 'r') as f:
            return json.load(f)

    def get_state_file(self, log_name):
        """Get state file for a specific log."""
        return self.state_dir / f"{log_name}.state"

    def get_last_pos(self, log_name):
        """Get last read position for log file."""
        state_file = self.get_state_file(log_name)
        if not state_file.exists():
            return 0
        try:
            with open(state_file, 'r') as f:
                return int(f.read().strip())
        except (ValueError, IOError):
            return 0

    def set_last_pos(self, log_name, pos):
        """Save last read position."""
        state_file = self.get_state_file(log_name)
        try:
            with open(state_file, 'w') as f:
                f.write(str(pos))
        except IOError:
            pass

    def read_new_lines(self, log_file):
        """Read new lines from log file since last position."""
        log_path = Path(log_file)
        if not log_path.exists():
            return []

        last_pos = self.get_last_pos(log_path.name)

        try:
            current_size = log_path.stat().st_size
            if current_size < last_pos:
                # Log file rotated/truncated
                last_pos = 0

            if current_size > last_pos:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(last_pos)
                    new_lines = f.readlines()
                    self.set_last_pos(log_path.name, current_size)
                    return new_lines
        except Exception as e:
            print(f"Error reading {log_file}: {e}", file=sys.stderr)

        return []

    def process_logs(self, server_interface):
        """
        Main loop: read all configured logs, post new lines to channels.

        server_interface: Handle to CSC server for writing to channels
        """
        for log_mapping in self.config.get("logs", []):
            log_file = log_mapping["file"]
            channels = log_mapping["channels"]
            nick = log_mapping.get("nick", "SystemLog")

            new_lines = self.read_new_lines(log_file)

            for line in new_lines:
                line = line.strip()
                if not line:
                    continue

                # Format message with nick
                message = f"[{nick}] {line}"

                # Post to all configured channels
                for channel in channels:
                    server_interface.write_to_channel(channel, message, from_nick=nick)

    def run_daemon(self, server_interface, poll_interval=10):
        """Run monitoring loop continuously."""
        while True:
            try:
                self.process_logs(server_interface)
            except Exception as e:
                print(f"Error in monitoring loop: {e}", file=sys.stderr)
            time.sleep(poll_interval)
```

### 2. Configuration File (log_monitor.json)

```json
{
  "enabled": true,
  "poll_interval": 10,
  "state_dir": "/opt/csc/tools/log_monitor_state",

  "logs": [
    {
      "name": "pm-journal",
      "file": "workorders/wip/pm-execution-journal.md",
      "channels": ["#pm"],
      "nick": "PM",
      "enabled": true
    },
    {
      "name": "queue-worker",
      "file": "logs/queue-worker.log",
      "channels": ["#queue-worker"],
      "nick": "QueueWorker",
      "enabled": true
    },
    {
      "name": "test-runner",
      "file": "logs/test-runner.log",
      "channels": ["#test-runner", "#dev"],
      "nick": "TestRunner",
      "enabled": true
    },
    {
      "name": "server",
      "file": "logs/server.log",
      "channels": ["#server-events"],
      "nick": "Server",
      "enabled": true
    }
  ]
}
```

### 3. Server Integration

Modify `packages/csc-server/csc_server/server.py` to:

```python
class Server:
    def __init__(self):
        # ... existing init ...
        self.log_monitor = None
        self.start_log_monitor()

    def start_log_monitor(self):
        """Start internal log monitoring."""
        try:
            from tools.log_monitor import LogMonitor
            self.log_monitor = LogMonitor("log_monitor.json")
            # Run in background thread
            import threading
            thread = threading.Thread(
                target=self.log_monitor.run_daemon,
                args=(self,),
                daemon=True
            )
            thread.start()
        except Exception as e:
            self.logger.warning(f"Log monitor failed to start: {e}")

    def write_to_channel(self, channel_name, message, from_nick="SystemLog"):
        """
        Internal method: write a message to a channel from a system nick.
        No IRC client needed - message injected directly into server.
        """
        if channel_name not in self.channels:
            # Create channel if it doesn't exist
            self.create_channel(channel_name)

        channel = self.channels[channel_name]

        # Create synthetic message as if from from_nick
        synthetic_message = f":{from_nick} PRIVMSG {channel_name} :{message}"

        # Broadcast to all users in channel
        for user in channel.members:
            client_addr = user.client_addr
            if client_addr in self.clients:
                self.send_to_client(client_addr, synthetic_message)

        # Optionally log to persistence
        if self.history:
            self.history.add_message(channel_name, from_nick, message)
```

### 4. NickServ Registration

Reserve system nicks in `storage/opers.json`:

```json
{
  "reserved_nicks": {
    "PM": "system",
    "QueueWorker": "system",
    "TestRunner": "system",
    "Server": "system"
  }
}
```

Modify `packages/csc-server/server_message_handler.py` to reject NICK changes to reserved nicks:

```python
def handle_nick(self, client_addr, new_nick):
    """Handle NICK command - reject if reserved."""
    reserved = self.server.reserved_nicks
    if new_nick.lower() in reserved:
        # Reject: nick is reserved
        self.send_reply(client_addr, 433, new_nick, "Nickname is reserved")
        return

    # ... existing nick handling ...
```

## Configuration Mapping

### Example: PM Monitoring

```json
{
  "name": "pm-journal",
  "file": "workorders/wip/pm-execution-journal.md",
  "channels": ["#pm"],
  "nick": "PM",
  "enabled": true
}
```

**What happens:**
1. Monitor reads `workorders/wip/pm-execution-journal.md`
2. New lines → Posted to `#pm` channel
3. Messages appear FROM nick "PM"
4. All users in #pm see: `<PM> [new log line]`

### Example: Multi-Channel Log

```json
{
  "name": "server-events",
  "file": "logs/server.log",
  "channels": ["#admin", "#monitoring", "#dev"],
  "nick": "Server",
  "enabled": true
}
```

**What happens:**
1. Monitor reads `logs/server.log`
2. Each new line posted to #admin, #monitoring, and #dev
3. All users in those channels see server events in real-time

## Setup Steps

### 1. Create log_monitor.json

```bash
cat > log_monitor.json << 'EOF'
{
  "enabled": true,
  "poll_interval": 10,
  "state_dir": "/opt/csc/tools/log_monitor_state",
  "logs": [
    {
      "name": "pm-journal",
      "file": "workorders/wip/pm-execution-journal.md",
      "channels": ["#pm"],
      "nick": "PM",
      "enabled": true
    }
  ]
}
EOF
```

### 2. Create Channels

Server auto-creates channels on first message, or pre-create:
```
/msg chanserv CREATE #pm
/msg chanserv SET #pm TOPIC "PM execution log"
```

### 3. Reserve Nicks

Add to `storage/opers.json`:
```json
"reserved_nicks": {
  "PM": "system",
  "QueueWorker": "system"
}
```

### 4. Start Server

Log monitor starts automatically when server starts.

## Usage

### Monitor PM Decisions

```
/join #pm
```

See messages like:
```
<PM> === Agent Selection ===
<PM> - gemini-3-pro assigned to fix_regex (simple)
<PM> *** CASCADE: infra change → test fixes triggered
```

### Monitor Multiple Logs

Join multiple channels:
```
/join #pm
/join #queue-worker
/join #test-runner
/join #server-events
```

Each channel streams its own log in real-time.

## Configuration Options

### Log Entry

```json
{
  "name": "unique-name",          // Required: unique identifier
  "file": "path/to/log.txt",      // Required: file to monitor
  "channels": ["#channel"],       // Required: channels to post to (array)
  "nick": "NickName",             // Required: sender nick
  "enabled": true,                // Optional: disable this log (default: true)
  "max_lines_per_poll": 100,      // Optional: limit per cycle
  "filter": "ERROR|WARN",         // Optional: regex filter (only matching lines)
  "prefix": "[LOG]"               // Optional: prefix all lines
}
```

## Performance

- **Polling:** Every 10 seconds (configurable)
- **State tracking:** One .state file per log (minimal overhead)
- **Memory:** O(1) - doesn't buffer, streams directly
- **Network:** Only sends new lines (efficient)

## Advantages

✅ **Flexible**: Configure any file-to-channel mapping
✅ **No bot setup**: Internal to server, no IRC client needed
✅ **No user conflict**: Reserved nicks are system-level
✅ **Scalable**: Add more logs by just editing JSON
✅ **Real-time**: Streams updates as they happen
✅ **Persistent**: Messages logged to channel history
✅ **Cross-channel**: One log can stream to many channels

## Testing

```bash
# 1. Start server
csc-server

# 2. Connect IRC client
irc-client

# 3. Join #pm
/join #pm

# 4. Trigger PM activity
agent assign test.md haiku

# 5. See in #pm
<PM> [log line from pm-execution-journal.md]
```

## Files Modified

- `tools/syslog_monitor.py` → Rename to `tools/log_monitor.py` (generalize)
- `log_monitor.json` (new configuration file)
- `packages/csc-server/csc_server/server.py` (add log monitor integration)
- `packages/csc-server/server_message_handler.py` (reject reserved nicks)
- `storage/opers.json` (reserve system nicks)

## Success Criteria

- [X] Generic log monitor created (configurable files)
- [X] JSON configuration supports many-to-many mapping
- [X] Server integrates log monitor (starts on boot)
- [X] Messages written directly to channels (no IRC client)
- [X] System nicks reserved in nickserv
- [X] Real-time streaming (new lines appear within 10s)
- [X] Multiple logs to multiple channels work correctly
- [X] Channel history persists messages
- [X] No UI/client setup needed for users
