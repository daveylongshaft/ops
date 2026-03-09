# Enhance Platform Layer - Path Resolution & System Detection

## Objective

Extend `packages/csc-service/csc_service/shared/platform.py` to provide:
1. **System Detection**: OS, filesystem type, hostname
2. **Path Resolution**: Auto-discover CSC_ROOT once
3. **Prepared Path Prefixes**: All common CSC directories pre-computed
4. **Single Source of Truth**: Sub-modules use platform-prepared paths, not discovering independently

## Problem Statement

Currently:
- ❌ Server has hardcoded `/opt/csc/` (breaks on Windows)
- ❌ Queue-worker independently discovers CSC_ROOT
- ❌ Multiple modules use relative paths inconsistently
- ❌ No platform detection (OS, fs type, hostname)
- ❌ Each module implements its own path discovery

Result: **Cross-platform paths broken**, path inconsistency, redundant code.

## Solution: Centralized Platform Layer

### 1. System Detection Properties

Add to `Platform` class:

```python
class Platform:
    @property
    def os_name(self):
        """Return OS identifier: 'windows', 'linux', 'macos', 'android'"""
        return self._detect_os()

    @property
    def fs_type(self):
        """Return filesystem type: 'ntfs', 'ext4', 'apfs', etc."""
        return self._detect_fs_type()

    @property
    def hostname(self):
        """Return system hostname"""
        return socket.gethostname()

    @property
    def path_separator(self):
        """Return path separator: '/' or '\\'"""
        return os.sep

    def _detect_os(self):
        """Detect operating system."""
        system = _platform.system()
        if system == "Windows":
            return "windows"
        elif system == "Darwin":
            return "macos"
        elif system == "Linux":
            # Check for Android via /system directory
            if os.path.exists("/system"):
                return "android"
            return "linux"
        else:
            return "unknown"

    def _detect_fs_type(self):
        """Detect filesystem type."""
        try:
            if self.os_name == "windows":
                # Use 'vol' command on Windows
                result = subprocess.run(
                    ["vol", "C:"],
                    capture_output=True, text=True, timeout=5
                )
                if "NTFS" in result.stdout:
                    return "ntfs"
                elif "FAT" in result.stdout:
                    return "fat32"
            else:
                # Use 'df -T' on Unix
                result = subprocess.run(
                    ["df", "-T", "/"],
                    capture_output=True, text=True, timeout=5
                )
                lines = result.stdout.split('\n')
                if len(lines) > 1:
                    return lines[1].split()[1]
        except Exception:
            pass
        return "unknown"
```

### 2. CSC Root Discovery (Once at Startup)

```python
@property
def csc_root(self):
    """Discover CSC project root (contains CLAUDE.md or csc-service.json)."""
    if hasattr(self, '_csc_root_cache'):
        return self._csc_root_cache

    # Start from this file's location
    current = Path(__file__).resolve()

    # Walk up to find CLAUDE.md or csc-service.json
    for _ in range(15):
        if (current / "CLAUDE.md").exists() or (current / "csc-service.json").exists():
            self._csc_root_cache = current
            return current
        if current == current.parent:
            break
        current = current.parent

    # Fallback: use current working directory
    self._csc_root_cache = Path.cwd()
    return self._csc_root_cache
```

### 3. Prepared Path Properties

```python
@property
def logs_dir(self):
    """Get logs directory (absolute path)."""
    return (self.csc_root / "logs").resolve()

@property
def storage_dir(self):
    """Get storage directory (absolute path)."""
    return (self.csc_root / "storage").resolve()

@property
def workorders_dir(self):
    """Get workorders directory (handles workorders/ or prompts/ fallback)."""
    workorders = self.csc_root / "workorders"
    prompts = self.csc_root / "prompts"
    if workorders.exists():
        return workorders.resolve()
    return prompts.resolve()

@property
def agents_dir(self):
    """Get agents directory."""
    return (self.csc_root / "agents").resolve()

@property
def tools_dir(self):
    """Get tools directory."""
    return (self.csc_root / "tools").resolve()

@property
def bin_dir(self):
    """Get bin directory."""
    return (self.csc_root / "bin").resolve()

@property
def packages_dir(self):
    """Get packages directory."""
    return (self.csc_root / "packages").resolve()

@property
def csc_service_dir(self):
    """Get csc-service package directory."""
    return (self.packages_dir / "csc-service").resolve()

# Subdirectories under workorders
@property
def ready_dir(self):
    return (self.workorders_dir / "ready").resolve()

@property
def wip_dir(self):
    return (self.workorders_dir / "wip").resolve()

@property
def done_dir(self):
    return (self.workorders_dir / "done").resolve()

@property
def hold_dir(self):
    return (self.workorders_dir / "hold").resolve()
```

### 4. Singleton Access Pattern

```python
# Global instance (initialized once)
_platform_instance = None

def get_platform():
    """Get global platform instance (singleton)."""
    global _platform_instance
    if _platform_instance is None:
        _platform_instance = Platform()
        _platform_instance._initialize()  # Detect everything at startup
    return _platform_instance
```

## Usage in Sub-modules

### Server (before - broken)
```python
syslog_script = "/opt/csc/tools/syslog_monitor.py"  # ❌ Hardcoded
```

### Server (after - correct)
```python
from csc_service.shared.platform import get_platform

class Server:
    def __init__(self):
        self.platform = get_platform()
        self.syslog_script = self.platform.tools_dir / "syslog_monitor.py"
        self.log_file = self.platform.logs_dir / "server.log"
        self.storage_dir = self.platform.storage_dir
```

### Queue Worker (before - independent discovery)
```python
# Had to walk up directory tree
csc_root = Path(__file__).resolve().parent.parent.parent
```

### Queue Worker (after - uses platform)
```python
from csc_service.shared.platform import get_platform

platform = get_platform()
csc_root = platform.csc_root
logs_dir = platform.logs_dir
workorders_dir = platform.workorders_dir
```

## Files Modified

1. **packages/csc-service/csc_service/shared/platform.py**
   - Add `os_name` property
   - Add `fs_type` property
   - Add `hostname` property
   - Add `path_separator` property
   - Add `csc_root` property (discovery logic)
   - Add all prepared path properties
   - Add `_detect_os()` method
   - Add `_detect_fs_type()` method
   - Add singleton getter: `get_platform()`

2. **packages/csc-service/csc_service/server/server.py**
   - Replace hardcoded `/opt/csc/` with `platform.tools_dir`
   - Use `platform.logs_dir` for log files
   - Use `platform.storage_dir` for storage JSON files

3. **packages/csc-service/csc_service/infra/queue_worker.py**
   - Replace manual CSC_ROOT discovery with `platform.csc_root`
   - Use `platform.logs_dir`, `platform.workorders_dir`, etc.

## Logging Detection

Add platform detection to startup logs:

```
[PLATFORM] OS: windows
[PLATFORM] FS Type: ntfs
[PLATFORM] Hostname: davey-machine
[PLATFORM] Path Sep: \
[PLATFORM] CSC Root: C:\csc
[PLATFORM] Logs: C:\csc\logs
[PLATFORM] Storage: C:\csc\storage
```

## Success Criteria

- [X] Platform class detects OS (windows, linux, macos, android)
- [X] Platform class detects FS type (ntfs, ext4, apfs, etc.)
- [X] Platform class detects hostname
- [X] Platform provides path_separator (/ or \)
- [X] CSC_ROOT discovered once at startup (cached)
- [X] All common CSC directories available as properties
- [X] Server uses platform.tools_dir (no more /opt/csc/)
- [X] Queue worker uses platform paths
- [X] Singleton pattern prevents multiple discoveries
- [X] All paths are absolute (resolved)
- [X] Works on Windows, Linux, macOS, Android

## Testing

```bash
# Start server
csc-server

# Check logs for platform detection
tail logs/server.log | grep PLATFORM

# Verify paths are correct for the OS
# On Windows: C:\csc\...
# On Linux: /opt/csc/... or /home/user/csc/...

# Test all sub-modules can access platform
python -c "from csc_service.shared.platform import get_platform; p = get_platform(); print(f'OS: {p.os_name}'); print(f'Logs: {p.logs_dir}')"
```

## Benefits

✅ **One source of truth** for all paths
✅ **Auto-discovers CSC_ROOT** across platforms
✅ **No hardcoded paths** (fixes Windows issues)
✅ **System detection** (OS, FS type, hostname available)
✅ **Consistent paths** across all sub-modules
✅ **Platform-aware** (/ vs \ handled automatically)
✅ **Caching** (discovery happens once)
✅ **Singleton pattern** (prevents redundant detection)
