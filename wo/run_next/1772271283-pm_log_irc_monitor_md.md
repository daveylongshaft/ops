# PM Log IRC Monitor - Real-Time PM Observability

## Objective

Create an IRC bot service that:
1. Monitors `workorders/wip/pm-execution-journal.md` for new lines
2. Posts new PM decisions to `#pm` channel on CSC IRC server
3. Allows all connected AIs (claude, gemini, chatgpt, etc.) to monitor PM activity
4. Works with linked/federated CSC servers across multiple sites

## Architecture

### New Component: PM Monitor Bot
```
Location: packages/csc-service/csc_service/clients/pm_monitor.py

Function:
  1. Connect to CSC IRC server (like csc-claude, csc-gemini)
  2. Join #pm channel (create if needed)
  3. Poll pm-execution-journal.md every 10 seconds
  4. Detect new lines (track file position)
  5. Post formatted updates to #pm
  6. Tag messages with [PM] prefix for easy filtering
```

### Integration Points

**1. Server Configuration**
- Add #pm channel to CSC server (auto-create if missing)
- Channel topic: "Project Manager execution log and decisions"
- Channel modes: +nt (no external messages, topic only for ops)

**2. PM Monitor Entry Point**
```bash
# Start PM monitor bot
csc-pm-monitor                     # Run once (one poll cycle)
csc-pm-monitor --daemon            # Run continuously (poll every 10s)
csc-pm-monitor --install           # Install as background service
```

**3. Existing Bot Integration**
Could also embed in:
- csc-bridge (bridge bot already in IRC)
- Or create standalone pm_monitor.py client

Recommend: Standalone so it's lightweight and independent.

## Implementation Details

### File Monitoring

```python
class PMMonitor:
    def __init__(self, server_config):
        self.journal_path = Path("workorders/wip/pm-execution-journal.md")
        self.last_position = 0  # Track file position
        self.irc_client = None

    def poll_journal(self):
        """Check for new lines in PM journal."""
        if not self.journal_path.exists():
            return []

        with open(self.journal_path, 'r', encoding='utf-8') as f:
            f.seek(self.last_position)
            new_lines = f.readlines()
            self.last_position = f.tell()  # Save position for next poll

        return new_lines

    def format_message(self, lines):
        """Format PM journal lines for IRC posting."""
        messages = []
        current_section = None

        for line in lines:
            # Parse section headers
            if line.startswith("## "):
                current_section = line[3:].strip()
                messages.append(f"[PM] === {current_section} ===")

            # Parse decision lines
            elif line.startswith("- "):
                decision = line[2:].strip()
                messages.append(f"[PM] {decision}")

            # Parse cascading triggers
            elif "CASCADE" in line.upper() or "PRIORITY" in line.upper():
                messages.append(f"[PM] *** {line.strip()}")

        return messages

    def post_to_channel(self, messages):
        """Send formatted messages to #pm channel."""
        for msg in messages:
            self.irc_client.send_message("#pm", msg)
```

### IRC Client Connection

```python
# Inherit from existing CSC IRC client (like csc-claude base)
class PMMonitor(IRCClient):
    NICK = "PM"
    REALNAME = "Project Manager Monitor"

    def on_connect(self):
        """Join #pm on connection."""
        self.join_channel("#pm")
        self.send_topic("#pm", "PM execution log and decisions")

    def run_monitor_loop(self):
        """Main polling loop."""
        while True:
            new_lines = self.poll_journal()
            if new_lines:
                messages = self.format_message(new_lines)
                self.post_to_channel(messages)
            time.sleep(10)  # Poll every 10 seconds
```

### Message Format

Example PM decisions as seen in #pm:

```
[PM] === Agent Selection ===
[PM] - gemini-3-pro assigned to PROMPT_fix_regex.md (complexity: simple, cost: $0.01)
[PM] *** CASCADE: infra change detected → triggering test-fix regen
[PM] === Workorder Status ===
[PM] - PROMPT_fix_regex.md: ready → wip (assigned to gemini-3-pro)
[PM] - PROMPT_fix_persistence.md: wip → done (completed successfully)
[PM] === Agent Performance ===
[PM] - gemini-3-pro: 4/5 complete (80% success rate)
```

## Cross-Server Support

### Federated CSC Sites

If CSC servers are linked (e.g., site-a.csc and site-b.csc):

```
Site A (main)
├─ csc-server
├─ csc-claude
├─ csc-gemini
├─ PM monitor bot  ← reads workorders/pm-execution-journal.md
│
└─ #pm channel ← All AIs on site A join and see PM decisions

Site B (remote)
├─ csc-server
├─ csc-claude
├─ csc-gemini
└─ [network link to Site A]

When sites link:
- Site B #pm mirrors Site A #pm via server-to-server protocol
- All AIs across both sites see unified PM decisions
```

Configuration in csc-service.json:

```json
{
  "pm-monitor": {
    "enabled": true,
    "nick": "PM",
    "server": "localhost:9525",
    "channel": "#pm",
    "poll_interval": 10,
    "journal_path": "workorders/wip/pm-execution-journal.md",
    "federation": {
      "enabled": false,
      "remote_servers": ["site-b.csc:9525"]
    }
  }
}
```

## Features

### 1. Real-Time Monitoring
- Any AI joins #pm
- Sees PM decisions as they happen
- Can react/respond to PM assignments

### 2. Decision Audit Trail
- All PM decisions logged in IRC history
- Searchable via IRC client
- Full transparency for agents

### 3. Alert Triggering
- **High-priority alerts**: If infrastructure change detected
- **Cascade notifications**: When PM triggers cascading actions
- **Agent feedback**: Post completion status to #pm for visibility

### 4. Workorder Status
- Show: WO moving from ready → wip → done
- Show: Which agent assigned
- Show: Completion status

### 5. Agent Performance Metrics
- Post periodic summaries: "Agent X: 92% completion rate"
- Cost tracking: "This week: $14.32 spent across agents"
- Performance ranking

## Configuration

### csc-service.json

```json
{
  "pm-monitor": {
    "enabled": true,
    "nick": "PM",
    "realname": "Project Manager Monitor",
    "server": "${CSC_SERVER_HOST:localhost}",
    "port": "${CSC_SERVER_PORT:9525}",
    "channel": "#pm",
    "poll_interval": 10,
    "journal_path": "workorders/wip/pm-execution-journal.md",
    "max_message_length": 400,
    "batch_similar": true,
    "show_metrics": true,
    "show_cascades": true,
    "show_agent_assignments": true
  }
}
```

### Installation

```bash
# Add to startup scripts
csc-service --pm-monitor --daemon

# Or register as background service
csc-ctl install pm-monitor
csc-ctl config pm-monitor enabled true
```

## Monitoring in Practice

### User (AI or Human) Perspective

```
# Join CSC server
/server localhost 9525
/join #pm

# Watch PM decisions in real-time
PM: [PM] === Agent Selection ===
PM: [PM] - gemini-3-pro assigned to fix_regex (simple)
PM: [PM] *** CASCADE: test-runner triggered for auto-regen
PM: [PM] === Cascading Triggers ===
PM: [PM] - Created 15 test-fix WOs from test-runner output
PM: [PM] === Workorder Status ===
PM: [PM] - fix_regex: ready → wip
```

### Cross-Site Visibility

If servers are linked:

```
Site A #pm and Site B #pm show SAME messages (mirrored)
- Any AI anywhere sees unified PM decisions
- All sites trust Site A's PM
- Great for distributed teams
```

## Testing

1. **Start PM monitor**:
   ```bash
   csc-pm-monitor --daemon
   ```

2. **Connect IRC client**:
   ```bash
   /server localhost 9525
   /join #pm
   ```

3. **Trigger PM activity**:
   ```bash
   # In another terminal
   agent assign test-wo.md haiku  # Should trigger PM decision
   ```

4. **Verify in #pm**:
   ```
   [PM] === Agent Selection ===
   [PM] - haiku assigned to test-wo.md
   ```

5. **Test cross-server** (if configured):
   - Connect to Site B IRC
   - Join #pm
   - Trigger PM on Site A
   - Verify Site B sees the message

## Success Criteria

- [X] PM monitor bot connects and joins #pm
- [X] Detects new lines in pm-execution-journal.md
- [X] Posts formatted messages to #pm within 1-2 seconds
- [X] All connected AIs can see PM decisions
- [X] Cross-server mirroring works (if enabled)
- [X] No missed updates (file position tracking works)
- [X] Unicode cleanup applied (ASCII only)
- [X] Performance: <1% CPU, <10MB memory

## Integration Notes

- **Depends on**: CSC IRC server, pm-execution-journal.md updates
- **Affects**: Observability, agent decision-making (can react to PM in #pm)
- **Cross-platform**: Works on Windows, Linux, macOS
- **Lightweight**: Can run alongside other bots
