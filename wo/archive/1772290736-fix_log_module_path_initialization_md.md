# Fix Log Module - Path Initialization & Directory Creation

## Problem

The Log module (2nd in inheritance chain: Root → **Log** → Data → Version → Platform...) fails when trying to write logs:

```
CRITICAL: Failed to write to log file 'Server.log': [Errno 2] No such file or directory: 'Server.log'
```

**Root causes:**
1. Log module sets `self.log_file = f"{self.name}.log"` (just filename, no path)
2. Tries to `open(self.log_file, "a")` without ensuring directory exists
3. Doesn't have platform context to know where logs/ directory should be
4. Relative path assumes logs are in current working directory (wrong)

## Architectural Issue

The Log module is too early in the inheritance chain to have platform context:
```
Root → Log → Data → Version → Platform → Network → Service
       ↑ (too early, Platform hasn't been initialized yet)
```

Log module can't know CSC_ROOT or where logs/ directory should be.

## Solution: Lazy Initialization Pattern

### 1. Modify Log.__init__()

```python
class Log(Root):
    def __init__(self, server=None):
        super().__init__()
        self.name = "log"
        self._log_file = None  # Lazy initialization
        self._platform = None  # Cache platform reference
```

### 2. Add log_file Property

```python
@property
def log_file(self):
    """Get log file path, initializing from platform if needed."""
    if self._log_file is None:
        # Try to get platform context
        try:
            from csc_service.shared.platform import get_platform
            self._platform = get_platform()
            logs_dir = self._platform.logs_dir
            logs_dir.mkdir(parents=True, exist_ok=True)  # ← CREATE DIRECTORY
            self._log_file = str(logs_dir / f"{self.name}.log")
        except Exception:
            # Fallback: use current directory
            self._log_file = f"{self.name}.log"
    return self._log_file

@log_file.setter
def log_file(self, value):
    """Allow setting log file path explicitly."""
    self._log_file = value
```

### 3. Update log() Method

```python
def log(self, message: str):
    """Log message with directory creation."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    class_name = self.__class__.__name__
    log_entry = f"[{timestamp}] [{class_name}] {message}\n"

    print(log_entry.strip())

    try:
        # Ensure log directory exists
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Append to log file
        with open(self.log_file, "a") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"CRITICAL: Failed to write to log file '{self.log_file}': {e}")
```

### 4. Import at Top

```python
from pathlib import Path
import time
from .root import Root
```

## Why This Works

1. **Lazy initialization**: Log file path determined when first log() is called
2. **Platform context**: By then, Platform has been initialized
3. **Directory creation**: Ensures logs/ directory exists before writing
4. **Fallback**: If Platform unavailable, uses simple filename
5. **Explicit override**: Server can still set log_file explicitly if needed

## File to Modify

**packages/csc-service/csc_service/shared/log.py**
- Change `self.log_file` to `self._log_file` (private)
- Add `@property log_file` (lazy-loaded)
- Add `@log_file.setter`
- Update `log()` method to create directories
- Import `Path` from pathlib

## Alternative: Early Configuration

If Log needs to know path at init time, Server could do:

```python
class Server(Log):
    def __init__(self):
        super().__init__()  # Log.__init__() runs first

        # After Platform is initialized, tell Log where to write
        from csc_service.shared.platform import get_platform
        platform = get_platform()
        self.log_file = str(platform.logs_dir / "server.log")

        # Now log() calls will use the correct path
        self.log("Server initialized")
```

## Testing

**Before fix:**
```bash
$ python -m csc_service.server
CRITICAL: Failed to write to log file 'Server.log': [Errno 2] No such file or directory
```

**After fix:**
```bash
$ python -m csc_service.server
[2026-02-28 08:58:00] [Server] Server initialized
$ ls logs/
server.log
$ cat logs/server.log
[2026-02-28 08:58:00] [Server] Server initialized
```

## Success Criteria

- [X] Log module uses lazy initialization for log_file
- [X] log() method creates logs/ directory if missing
- [X] Server starts without "Failed to write to log file" error
- [X] Logs written to correct location (logs/server.log, logs/bridge.log, etc.)
- [X] Works with platform layer when available
- [X] Falls back gracefully if platform unavailable
- [X] Server can explicitly override log_file if needed

## Related Issues

Once this is fixed, these should also work:
- `packages/csc-service/csc_service/server/server.py` (line 53, 68) - Remove manual path override
- `packages/csc-service/csc_service/bridge/` - Will inherit working log handling
- All other subclasses of Log - Automatic log file handling

## Impact

✅ Server can start and log successfully
✅ All subclasses inherit working logging
✅ Logs go to correct location across platforms
✅ No more "Failed to write to log file" errors
