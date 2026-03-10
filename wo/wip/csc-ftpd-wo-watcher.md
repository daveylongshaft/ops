---
role: feature
priority: P1
agent: gemini-3.1-pro-preview
depends: csc-ftpd-distributed-filesystem
---

# csc-ftpd: ops/wo/ Filesystem Watcher + Master Push Sync

## Context

`ops/` is now a git submodule (`daveylongshaft/ops.git`) and `ops/wo/` is the
canonical workorder queue used by all nodes. The csc-ftpd architecture (designed
in `ops/wo/done/csc-ftpd-distributed-filesystem.md`) defines master/slave FTP
sync. This WO implements the filesystem watcher that triggers that sync.

Each CSC node runs a watcher process that monitors `ops/wo/` for any filesystem
change. When a change is detected it pushes through the FTP master (fahu), which
replicates to all registered slave nodes. The result: every node's `ops/wo/` is
always in sync within seconds of any change anywhere.

## What To Build

### 1. `irc/packages/csc-service/csc_service/infra/wo_watcher.py`

A cross-platform daemon that watches `ops/wo/` and triggers sync on change.

```python
class WoWatcher:
    """Monitors ops/wo/ and pushes changes through the FTP master."""

    def __init__(self, wo_dir, ftp_master_host, ftp_master_port=9521):
        ...

    def start(self):
        """Start watching. Blocks (run in thread or as daemon)."""
        ...

    def on_change(self, changed_path):
        """Called when any file in ops/wo/ changes. Triggers FTP push."""
        ...
```

**Detection strategy (in priority order):**
1. `inotify` (Linux kernel, zero overhead) via `inotify_simple` or `/proc/sys/fs/inotify`
2. `watchdog` library (cross-platform, polling fallback)
3. Pure polling fallback — stat() every 5s, no external deps

**Debounce:** batch changes within a 500ms window before pushing (avoid thrashing
on rapid multi-file operations like queue_worker moving WO from wip/ to done/).

### 2. FTP push protocol

When a change is detected, the watcher:

1. Calculates SHA-256 hash + size of changed file(s)
2. Connects to FTP master via `ftplib.FTP_TLS` (AUTH TLS, port 9521)
3. Authenticates as the node's agent user (cert from OpenVPN CA on fahu)
4. Uploads changed file to mirror path on master: `wo/<subdir>/<filename>`
5. Master replicates to all slaves immediately (via existing ftpd slave protocol)
6. For deletions: sends `DELE` command to master

**Filelist hash sync:** After any push, recalculate the `ops/wo/` filelist hash
(SHA-256 of sorted `filename:size:mtime` entries) and upload to
`wo/.filelist.hash` on master. Slaves compare this hash on startup and request
a delta if they're behind.

### 3. `irc/packages/csc-service/csc_service/infra/wo_sync_client.py`

Slave-side sync client. On startup (or when filelist hash mismatch detected):

1. Fetch `wo/.filelist.hash` from master
2. Compare to local hash
3. If mismatch: request full delta listing from master
4. Download only changed/missing files

### 4. csc-ctl integration

```
csc-ctl enable wo-watcher      # start watching ops/wo/ and auto-syncing
csc-ctl status wo-watcher      # show last sync time, hash, connected slaves
csc-ctl disable wo-watcher     # stop (manual git sync still works)
```

### 5. `irc/tests/test_wo_watcher.py`

Tests:
- `test_detects_new_file` — create file in ops/wo/ready/, verify on_change called
- `test_detects_deletion` — delete file, verify on_change called
- `test_debounce` — rapid changes batched into single callback
- `test_filelist_hash` — hash changes when file added/removed/modified
- `test_ftp_push_mock` — mock FTP server, verify correct STOR/DELE commands sent
- `test_slave_delta_sync` — mock master, slave fetches only changed files

## Configuration

Add to `etc/platform.json` under `"runtime"`:
```json
{
  "runtime": {
    "wo_watcher": {
      "enabled": false,
      "ftp_master_host": "fahu.facingaddictionwithhope.com",
      "ftp_master_port": 9521,
      "watch_dir": "ops/wo",
      "debounce_ms": 500,
      "poll_interval_s": 5
    }
  }
}
```

## Rules

- Do NOT implement the full FTP server (that's a separate WO)
- The watcher only needs a thin FTP client (ftplib, stdlib)
- inotify is preferred on Linux; polling is the fallback — support both
- Watcher runs as a csc-ctl managed service, not a cron job
- No Task Scheduler on Windows — use threading + polling there
- Port 9521 is the CSC FTP control port (CSC uses 9520-9529 range)
- Must work on Windows, Linux, and macOS — use `platform.system()` to branch where needed
- `inotify` is Linux-only; Windows uses polling via `threading.Timer` loop; macOS uses `watchdog` or polling
- `hasattr(os, 'mkfifo')` pattern for any POSIX-only calls
- Write tests, do not run them

## Files To Create

- `irc/packages/csc-service/csc_service/infra/wo_watcher.py`
- `irc/packages/csc-service/csc_service/infra/wo_sync_client.py`
- `irc/tests/test_wo_watcher.py`
- Update `etc/platform.json` schema docs in `docs/platform.md`


--- Agent Log ---
Invoking: gemini -y -m gemini-2.5-pro -p " "
/usr/local/lib/node_modules/@google/gemini-cli/dist/index.js:7
import './src/gemini.js';
       ^^^^^^^^^^^^^^^^^

SyntaxError: Unexpected string
    at Module._compile (internal/modules/cjs/loader.js:723:23)
    at Object.Module._extensions..js (internal/modules/cjs/loader.js:789:10)
    at Module.load (internal/modules/cjs/loader.js:653:32)
    at tryModuleLoad (internal/modules/cjs/loader.js:593:12)
    at Function.Module._load (internal/modules/cjs/loader.js:585:3)
    at Function.Module.runMain (internal/modules/cjs/loader.js:831:12)
    at startup (internal/bootstrap/node.js:283:19)
    at bootstrapNodeJSCore (internal/bootstrap/node.js:623:3)

[INFO] Agent execution completed
[INFO] Log: /opt/csc/ops/logs/gemini-2.5-pro_1773106893.log


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)


--- Agent Log ---
Invoking: gemini -y -m gemini-2.5-pro -p " "
/usr/local/lib/node_modules/@google/gemini-cli/dist/index.js:7
import './src/gemini.js';
       ^^^^^^^^^^^^^^^^^

SyntaxError: Unexpected string
    at Module._compile (internal/modules/cjs/loader.js:723:23)
    at Object.Module._extensions..js (internal/modules/cjs/loader.js:789:10)
    at Module.load (internal/modules/cjs/loader.js:653:32)
    at tryModuleLoad (internal/modules/cjs/loader.js:593:12)
    at Function.Module._load (internal/modules/cjs/loader.js:585:3)
    at Function.Module.runMain (internal/modules/cjs/loader.js:831:12)
    at startup (internal/bootstrap/node.js:283:19)
    at bootstrapNodeJSCore (internal/bootstrap/node.js:623:3)

[INFO] Agent execution completed
[INFO] Log: /opt/csc/ops/logs/gemini-2.5-pro_1773106893.log


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)
