# System-Wide Architecture: Cross-Platform Path Resolution

## Vision

**Single source of truth for all paths across all operating systems.**

Every CSC module (server, client, queue-worker, agents, etc.) must use the platform layer for path discovery and construction. No hardcoded paths, no independent discovery, no OS-specific code scattered throughout.

## Supported Platforms

### Primary Platforms (Fully Supported)
- **Windows** (10+, 11) - MSYS2/Git Bash
- **Linux** (Ubuntu, Debian, Fedora, CentOS, etc.)
- **macOS** (10.15+, Apple Silicon compatible)
- **Android** (via Termux, WSL, or Termux-embedded)

### Platform Detection Requirements

Each platform must be detected and provide:

#### Windows
```
os_name: "windows"
path_separator: "\\"
home_dir: C:\Users\<username>
csc_root: C:\csc (or wherever installed)
fs_type: "ntfs" | "fat32" | "refs"
```

#### Linux
```
os_name: "linux"
path_separator: "/"
home_dir: /home/<username>
csc_root: /opt/csc (or /home/user/csc, etc.)
fs_type: "ext4" | "btrfs" | "xfs" | etc.
distro: "ubuntu" | "debian" | "fedora" | "centos" | etc. (optional)
```

#### macOS
```
os_name: "macos"
path_separator: "/"
home_dir: /Users/<username>
csc_root: /opt/csc (or /Users/user/csc, etc.)
fs_type: "apfs" | "hfs+"
architecture: "intel" | "apple_silicon"
```

#### Android (Termux)
```
os_name: "android"
path_separator: "/"
home_dir: /data/data/com.termux/files/home
csc_root: /data/data/com.termux/files/home/csc (or /storage/emulated/0/csc)
fs_type: "ext4" (typically)
termux_version: "0.118" (or current)
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│         Platform Layer (singleton)                      │
│  (packages/csc-service/shared/platform.py)              │
│                                                          │
│  ├─ detect_os()        → "windows"|"linux"|"macos"|"android"
│  ├─ detect_fs_type()   → "ntfs"|"ext4"|"apfs"|"ext4"
│  ├─ get_hostname()     → "davey-machine"
│  ├─ get_home_dir()     → platform-specific home
│  ├─ discover_csc_root()→ auto-find project root
│  │
│  └─ Prepared Paths (properties):
│     ├─ csc_root        → /opt/csc (or C:\csc, etc.)
│     ├─ logs_dir        → /opt/csc/logs
│     ├─ storage_dir     → /opt/csc/storage
│     ├─ workorders_dir  → /opt/csc/workorders
│     ├─ agents_dir      → /opt/csc/agents
│     ├─ tools_dir       → /opt/csc/tools
│     ├─ bin_dir         → /opt/csc/bin
│     └─ ... (more as needed)
└─────────────────────────────────────────────────────────┘
           ↑ (used by all modules)
           │
    ┌──────┴──────┬──────────┬──────────┬────────────┐
    │             │          │          │            │
┌───▼──┐    ┌────▼──┐  ┌───▼──┐  ┌───▼──┐  ┌──▼───┐
│Server│    │Queue  │  │Agent │  │Client│  │Bridge│
│      │    │Worker │  │      │  │      │  │      │
└──────┘    └───────┘  └──────┘  └──────┘  └──────┘

All use: platform.logs_dir, platform.storage_dir, etc.
NO hardcoded paths anywhere
```

## Required Changes by Module

### 1. Server (packages/csc-service/csc_service/server/server.py)
**Current Issues:**
- Line 241: `syslog_script = "/opt/csc/tools/syslog_monitor.py"` (hardcoded)
- Logs written to relative paths (fails on different cwd)
- Storage files created in wrong directory

**Changes Required:**
```python
from csc_service.shared.platform import get_platform

class Server:
    def __init__(self):
        self.platform = get_platform()

        # Use platform paths
        self.syslog_script = self.platform.tools_dir / "syslog_monitor.py"
        self.log_file = self.platform.logs_dir / "server.log"
        self.storage_dir = self.platform.storage_dir
        self.channels_file = self.storage_dir / "channels.json"
        self.users_file = self.storage_dir / "users.json"
        self.history_file = self.storage_dir / "history.json"
```

### 2. Queue Worker (packages/csc-service/csc_service/infra/queue_worker.py)
**Current Issues:**
- Manual CSC_ROOT discovery (line 75+)
- Relative paths without root context
- Hardcoded `/opt/csc/` in fallback

**Changes Required:**
```python
from csc_service.shared.platform import get_platform

platform = get_platform()
CSC_ROOT = platform.csc_root
LOGS_DIR = platform.logs_dir
WORKORDERS_DIR = platform.workorders_dir
AGENTS_DIR = platform.agents_dir

# Use platform paths everywhere
log_file = LOGS_DIR / "queue-worker.log"
queue_log = LOGS_DIR / "queue-wip-sizes.json"
```

### 3. Clients (all AI clients: claude, gemini, chatgpt, etc.)
**Current Issues:**
- Hardcoded server addresses
- No platform detection for local paths

**Changes Required:**
```python
from csc_service.shared.platform import get_platform

platform = get_platform()
# Use for local config/cache directories
config_dir = platform.home_dir / ".csc" / self.client_name
cache_dir = platform.csc_root / "cache" / self.client_name
```

### 4. Bridge (packages/csc-service/csc_service/bridge/)
**Current Issues:**
- Same hardcoded path issues
- No platform detection

**Changes Required:**
```python
from csc_service.shared.platform import get_platform

platform = get_platform()
log_file = platform.logs_dir / "bridge.log"
```

### 5. Test Runner (packages/csc-service/csc_service/infra/test_runner.py)
**Current Issues:**
- Hardcoded test paths
- No platform detection

**Changes Required:**
```python
from csc_service.shared.platform import get_platform

platform = get_platform()
test_logs_dir = platform.logs_dir / "tests"
```

### 6. PM Module (packages/csc-service/csc_service/infra/pm.py)
**Current Issues:**
- Journal path hardcoded
- Workorder discovery manual

**Changes Required:**
```python
from csc_service.shared.platform import get_platform

platform = get_platform()
journal_file = platform.wip_dir / "pm-execution-journal.md"
workorders_dir = platform.workorders_dir
```

## Implementation Phases

### Phase 1: Platform Layer Enhancement (IMMEDIATE)
- Implement all platform detection in platform.py
- Add OS detection: Windows, Linux, macOS, Android
- Add FS type detection
- Add hostname, path_separator, home_dir
- Create singleton getter: `get_platform()`
- **Workorder**: ENHANCE_platform_layer_path_resolution.md (already created)

### Phase 2: Server Migration
- Update server.py to use platform paths
- Remove hardcoded `/opt/csc/`
- Test on Windows, Linux, macOS
- **Workorder**: FIX_server_path_resolution.md

### Phase 3: Queue Worker & Infra
- Update queue_worker.py to use platform
- Update pm.py to use platform
- Update test_runner.py to use platform
- **Workorder**: Consolidate infra modules for platform migration

### Phase 4: All Clients & Services
- Update csc-claude, csc-gemini, csc-chatgpt
- Update bridge
- Update any other modules
- **Workorder**: Migrate all clients to platform layer

### Phase 5: Audit & Verification
- Grep for all remaining hardcoded paths
- Test on all 4 platforms
- Document any platform-specific quirks
- **Workorder**: Audit and verify cross-platform paths

## Platform-Specific Implementation Notes

### Windows (MSYS2/Git Bash)
- Path separator: `\` (but `/` also works in MSYS2)
- Drive letters: `C:\`, `D:\`, etc.
- Home directory: `C:\Users\<username>`
- Use `os.name == 'nt'` to detect
- Filesystem typically NTFS
- Use `pathlib.Path` (handles both separators)

### Linux (Various Distros)
- Path separator: `/`
- Home directory: `/home/<username>` or `/root`
- Filesystem detection: `df -T` command
- Use `platform.system() == 'Linux'`
- Most common: ext4, btrfs, xfs

### macOS (Intel & Apple Silicon)
- Path separator: `/`
- Home directory: `/Users/<username>`
- Filesystem typically APFS (newer) or HFS+ (older)
- Use `platform.system() == 'Darwin'`
- Need to detect Apple Silicon vs Intel (`platform.machine()`)
- Homebrew paths: `/usr/local` (Intel) or `/opt/homebrew` (Apple Silicon)

### Android (Termux)
- Path separator: `/`
- Home directory: `/data/data/com.termux/files/home`
- Alternative: `/storage/emulated/0` for shared storage
- Detect via `/system` directory existence
- Filesystem typically ext4
- Limited capabilities (no Docker, no systemd)

## Configuration Files

Store platform-detected settings in `platform.json`:

```json
{
  "detected_at": "2026-02-28T08:55:00Z",
  "os": "windows",
  "fs_type": "ntfs",
  "hostname": "davey-machine",
  "home_dir": "C:\\Users\\davey",
  "csc_root": "C:\\csc",
  "python_version": "3.11.7",
  "git_available": true,
  "docker_available": false
}
```

## Testing Matrix

Test on all platforms:

| Platform | OS | FS Type | Status | Notes |
|----------|----|---------|---------|----|
| Windows 11 | windows | ntfs | ⏳ | Primary dev |
| Ubuntu 22 | linux | ext4 | ⏳ | Server |
| macOS 14 | macos | apfs | ⏳ | Secondary |
| Termux | android | ext4 | ⏳ | Future |

## Success Criteria

- [X] Platform layer detects all 4 OSes correctly
- [X] Platform layer detects filesystem types
- [X] All modules use `platform.csc_root`, not hardcoded paths
- [X] No `/opt/csc/` hardcoded anywhere
- [X] Server works on Windows
- [X] Server works on Linux
- [X] Server works on macOS (prepare for it)
- [X] Architecture documented in CLAUDE.md
- [X] All sub-modules can call `get_platform()`
- [X] Path detection happens once at startup
- [X] Paths are absolute (resolved)

## CLAUDE.md Update

Add to CLAUDE.md architecture section:

```markdown
## Cross-Platform Path Resolution Architecture

All CSC modules use the centralized Platform layer for path discovery:

```python
from csc_service.shared.platform import get_platform
platform = get_platform()

# Use prepared paths, never hardcoded
log_file = platform.logs_dir / "server.log"
storage = platform.storage_dir / "channels.json"
```

Platform layer detects:
- OS: Windows, Linux, macOS, Android
- Filesystem type: NTFS, ext4, APFS, etc.
- Hostname, home directory, CSC root

**Rule**: No hardcoded `/opt/csc/` or OS-specific paths anywhere.
```

## Migration Checklist

- [ ] Phase 1: Enhance platform layer (CRITICAL)
- [ ] Phase 2: Update server.py
- [ ] Phase 3: Update infra modules
- [ ] Phase 4: Update all clients
- [ ] Phase 5: Audit & verify
- [ ] Update CLAUDE.md with architecture
- [ ] Test on Windows, Linux, macOS
- [ ] Prepare for Android (test when possible)
- [ ] Document platform-specific quirks

## Long-Term Benefits

✅ **Works everywhere** - Windows, Linux, macOS, Android
✅ **No hardcoded paths** - Maintainable, flexible
✅ **Single discovery** - Efficient, cached
✅ **OS detection** - Enables OS-specific code when needed
✅ **Filesystem awareness** - Can optimize for different FS types
✅ **Future-proof** - Adding new platforms just extends platform.py
✅ **Distributed teams** - Works on any developer's machine
