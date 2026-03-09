# Update Documentation for csc-ctl Commands

## Task

Update CLAUDE.md and create docs/csc-ctl.md to document the full csc-ctl command set.

## What Changed

csc-ctl was extended with new commands. The documentation needs to reflect the actual working commands.

## Working Commands (verified)

```bash
# Status
csc-ctl status                    # Show all services + clients + poll interval
csc-ctl status <service>          # Single service status
csc-ctl show <service>            # Display service config (JSON)
csc-ctl show <service> <setting>  # Display specific setting

# Enable/Disable
csc-ctl enable <service>          # Enable a service
csc-ctl disable <service>         # Disable a service

# Config get/set
csc-ctl config <service> <setting>         # Get config value
csc-ctl config <service> <setting> <value> # Set config value
csc-ctl set <key> <value>                  # Set top-level config (shorthand)

# Export/Import
csc-ctl dump                      # Export full config as JSON
csc-ctl dump <service>            # Export single service config
csc-ctl import                    # Import config from stdin
csc-ctl import <service>          # Import config for single service

# Service lifecycle
csc-ctl restart <service>         # Graceful restart
csc-ctl restart <service> --force # Force kill + restart
csc-ctl install [service|all]     # Install scheduled tasks (Windows) / show cron (Unix)
csc-ctl remove [service|all]      # Remove scheduled tasks

# Manual cycle
csc-ctl cycle queue-worker        # Run one queue-worker cycle
csc-ctl cycle test-runner         # Run one test-runner cycle
csc-ctl cycle pm                  # Run one PM cycle
```

## Services

Known services: queue-worker, test-runner, pm, server, bridge
Known clients: gemini, claude, dmrbot, chatgpt

## Instructions

1. Update the "Common Commands" section in CLAUDE.md to include the full csc-ctl command reference
2. Replace any old/stale csc-ctl references in CLAUDE.md
3. Update SCHEDULER_SETUP.md to reference `csc-ctl install` instead of manual setup
4. Keep documentation concise and example-focused

## Config File

Config is stored in `csc-service.json` at project root. Format:
```json
{
  "poll_interval": 60,
  "enable_queue_worker": true,
  "enable_test_runner": false,
  "enable_pm": false,
  "enable_server": true,
  "enable_bridge": true,
  "clients": {
    "gemini": {"enabled": true, "auto_start": true},
    "claude": {"enabled": false}
  }
}
```

Journal progress to this WIP file. Write COMPLETE when done.

PID: 40568 agent: gemini-2.5-flash starting at 2026-02-25 19:58:22

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)

PID: 25376 agent: gemini-2.5-flash starting at 2026-02-25 20:06:59


--- AUDIT [2026-02-27 13:22] ---
INCOMPLETE
Pending:
  - Update CLAUDE.md with full csc-ctl command reference
  - Replace stale csc-ctl references in CLAUDE.md
  - Update SCHEDULER_SETUP.md to reference csc-ctl install
  - Create/update docs/csc-ctl.md with command documentation
  - Verify all documentation changes are in place
  - Add COMPLETE marker to workorder
Workorder has task definition and working command list but no work log entries or COMPLETE marker - agent started but never finished execution


DEAD END - Superseded by csc-ctl v1.0 rewrite (2026-02-27)
