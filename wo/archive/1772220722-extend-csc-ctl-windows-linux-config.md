---
requires: [python3, git]
platform: [windows, linux]
---

# Extend csc-ctl: Windows/Linux Support + Config Management + Service Control

## Summary

Extended `csc-ctl` to be a full cross-platform CLI for managing CSC services.

## Work Completed

### Implementation (Claude Opus 4.6 - 2026-02-25)

1. **Fixed broken imports** in `csc_ctl.py` - was using wrong relative import path
2. **Rewrote all command modules** to work with actual `csc-service.json` format:
   - `status_cmd.py` - Shows all services, clients, poll interval, config path
   - `config_cmd.py` - Get/set config, enable/disable services, dump/import, type coercion
   - `service_cmd.py` - restart/stop/start with cross-platform PID management, install/remove scheduled tasks, cycle subsystems
3. **Added missing commands**: `enable`, `disable`, `set` (shorthand), `cycle`
4. **Cross-platform service control**: Windows uses `taskkill`, Unix uses signals
5. **Cross-platform install**: Windows uses `schtasks`, Unix outputs crontab entries
6. **Config format mapping**: Maps service names to actual config keys (`queue-worker` → `enable_queue_worker`)
7. **Cycle command**: Actually instantiates and runs subsystem cycles (queue-worker, test-runner, pm)

### Commands Verified Working

```bash
csc-ctl status                          # Shows all services + clients
csc-ctl status queue-worker             # Single service status
csc-ctl show gemini                     # Client config display
csc-ctl enable pm                       # Enable service
csc-ctl disable pm                      # Disable service
csc-ctl set poll_interval 120           # Set top-level config
csc-ctl config queue-worker enabled     # Get config value
csc-ctl dump                            # Export full config as JSON
```

### Files Modified

- `packages/csc-service/csc_service/cli/csc_ctl.py` - Main CLI (fixed imports, added enable/disable/set/cycle)
- `packages/csc-service/csc_service/cli/commands/status_cmd.py` - Rewritten for actual config format
- `packages/csc-service/csc_service/cli/commands/config_cmd.py` - Rewritten with service key mapping
- `packages/csc-service/csc_service/cli/commands/service_cmd.py` - Full implementation (was stubs)
- `packages/csc-service/csc_service/config.py` - Already working (atomic writes, backup, env var support)

### Previous Work (Gemini-2.5-pro - 2026-02-25)

- Created initial CLI skeleton with argparse
- Created ConfigManager with atomic writes and backup
- Set up command module structure
- Status and config commands partially working
- Service commands were stubs

COMPLETE


--- AUDIT [2026-02-27 13:22] ---
INCOMPLETE
Pending:
  - No Work Log section with agent activity steps - only a narrative summary under 'Work Completed'
  - Missing COMPLETE marker at end of work log (has 'COMPLETE' but not as work log entry)
  - No evidence of actual testing - example commands listed but no test output/results shown
  - No verification that imports were actually fixed (claims 'fixed broken imports' but no before/after code shown)
  - No verification that cross-platform service control actually works (Windows taskkill, Unix signals claimed but untested)
  - No code diffs or file content shown to verify the 'rewritten' command modules
  - Lacks concrete evidence of testing on both Windows and Linux platforms despite platform tag
Workorder reads as a completion report/summary rather than an audit log with verified work steps and test results - missing documented evidence of actual implementation and testing


DEAD END - Superseded by csc-ctl v1.0 rewrite (2026-02-27)
