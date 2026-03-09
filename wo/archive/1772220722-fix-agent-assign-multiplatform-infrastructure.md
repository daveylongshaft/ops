=== Task: fix-agent-assign-multiplatform-infrastructure.md ===

---
requires: [python3, git]
platform: [windows, linux, macos, android]
---

# Fix agent assign Segfault + Build Multi-Platform CLI Infrastructure

## Critical Issues

1. **agent assign segfault** - Command fails with segmentation fault on Windows
2. **Hardcoded paths** - Scripts hardcode OS-specific paths (C:\, /home, etc)
3. **Platform detection** - No unified way to detect system capabilities and OS
4. **CLI portability** - Each script written for one OS, doesn't work elsewhere
5. **Data persistence** - Platform-specific config scattered across files

## Root Cause

Agent assign calls `subprocess.run()` for git clone in temp directory (lines 436-441). The segfault likely comes from:
- Subprocess not properly isolated from parent Python process
- Process creation differences between Windows/Linux
- Shell invocation differences (Windows needs `shell=True`, Linux doesn't)
- Path handling in subprocess calls (forward vs backslashes)

## Solution Architecture

### 1. Unified Platform Configuration (platform.json)

Store ALL platform-specific paths and settings in one place:

```json
{
  "system": {
    "platform": "windows|linux|macos|android",
    "is_windows": true/false,
    "is_unix": true/false,
    "shell": "cmd.exe|/bin/bash|/bin/zsh|/system/bin/sh",
    "path_separator": "\\|/",
    "line_ending": "\\r\\n|\\n"
  },
  "paths": {
    "project_root": "C:\\csc|/opt/csc|/home/user/csc",
    "temp_root": "C:\\Users\\user\\AppData\\Local\\Temp|/tmp|/var/tmp",
    "csc_agent_work": "C:\\Users\\user\\AppData\\Local\\Temp\\csc|/tmp/csc",
    "bin_dir": "C:\\csc\\bin|/opt/csc/bin",
    "workorders_dir": "C:\\csc\\workorders|/opt/csc/workorders",
    "agents_dir": "C:\\csc\\agents|/opt/csc/agents",
    "logs_dir": "C:\\csc\\logs|/opt/csc/logs"
  },
  "binaries": {
    "python": "python3|python",
    "git": "/usr/bin/git|C:\\Program Files\\Git\\bin\\git.exe",
    "bash": "/bin/bash|C:\\Program Files\\Git\\bin\\bash.exe",
    "cagent": "cagent|/usr/local/bin/cagent"
  },
  "subprocess_config": {
    "use_shell": false,
    "shell_for_piping": true,
    "start_new_session": true|false,
    "encoding": "utf-8",
    "errors": "replace"
  }
}
```

### 2. Subprocess Helper Module

**File**: `packages/csc-service/csc_service/shared/subprocess_helper.py`

```python
class SubprocessRunner:
    """Cross-platform subprocess execution with proper path and shell handling."""

    def __init__(self, platform_data=None):
        """Initialize with platform config."""
        self.platform_data = platform_data or Platform.load_platform_json()
        self.is_windows = self.platform_data.get('system', {}).get('is_windows', False)
        self.shell = self.platform_data.get('system', {}).get('shell')
        self.encoding = self.platform_data.get('subprocess_config', {}).get('encoding', 'utf-8')

    def run(self, cmd, cwd=None, needs_pipe=False, timeout=30):
        """
        Run command with proper platform handling.

        Args:
            cmd: Command as list: ["git", "clone", "url", "path"]
            cwd: Working directory (absolute path)
            needs_pipe: True if command uses pipes (|, &&, etc)
            timeout: Timeout in seconds

        Returns:
            CompletedProcess with stdout, stderr, returncode
        """
        # Convert list to shell command if pipes needed
        if needs_pipe:
            cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
            return subprocess.run(
                cmd_str,
                cwd=str(cwd) if cwd else None,
                shell=True,  # Required for pipes
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding=self.encoding,
                errors='replace'
            )
        else:
            # Direct execution without shell
            return subprocess.run(
                cmd,
                cwd=str(cwd) if cwd else None,
                shell=False,  # Safe direct execution
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding=self.encoding,
                errors='replace'
            )

    def run_in_session(self, cmd, cwd=None):
        """Run in new process session (for background services)."""
        kwargs = {
            'cwd': str(cwd) if cwd else None,
            'shell': False,
            'capture_output': True,
            'text': True,
            'encoding': self.encoding,
            'errors': 'replace'
        }

        # Only Unix supports start_new_session
        if not self.is_windows:
            kwargs['start_new_session'] = True

        return subprocess.run(cmd, **kwargs)
```

### 3. Fix agent_service.py assign() Method

**Problem**: Lines 436-441 use raw subprocess.run() without platform awareness

**Solution**:
- Use SubprocessRunner helper
- Detect Windows vs Unix
- Handle shell differences
- Proper error handling
- No segfault-prone direct process spawning

```python
def assign(self, prompt_filename: str) -> str:
    # ... existing code ...

    # Create isolated agent work directory in system temp
    try:
        from csc_service.shared.subprocess_helper import SubprocessRunner

        platform = Platform()
        agent_work_base = platform.agent_work_base
        if not agent_work_base:
            return "Platform agent_work_base not available. Check platform.json"

        # Create directory structure
        agent_work_dir = agent_work_base / selected
        repo_clone_path = agent_work_dir / "repo"

        agent_work_dir.mkdir(parents=True, exist_ok=True)
        repo_clone_path.mkdir(parents=True, exist_ok=True)

        # Use platform-aware subprocess runner
        runner = SubprocessRunner()

        # Git clone with proper error handling
        result = runner.run(
            ["git", "clone", str(self.PROJECT_ROOT), str(repo_clone_path)],
            timeout=60
        )

        if result.returncode != 0:
            self.log(f"Git clone failed: {result.stderr}")
            return f"Failed to create agent work directory: git clone failed"

        # ... rest of code ...
```

### 4. Fix bin/csc-ctl to Use Platform Paths

Current problem: csc-ctl.bat hardcodes Windows paths, doesn't work on Linux

Solution:
- Rewrite as Python CLI (like agent)
- Load paths from platform.json
- Use SubprocessRunner for all subprocess calls
- Works on all OSes

### 5. Multi-Platform Path Handling Utilities

**File**: `packages/csc-service/csc_service/shared/path_helper.py`

```python
class CrossPlatformPath:
    """Handle paths that work across Windows/Linux/macOS."""

    @staticmethod
    def normalize_for_command(path):
        """Convert path for use in subprocess commands."""
        # On Windows with Unix-style tools (Git Bash), use forward slashes
        # On native Windows (cmd.exe), use backslashes
        # On Unix, always use forward slashes

        if sys.platform == 'win32':
            # Check if we're in Git Bash or native Windows
            if 'MSYSTEM' in os.environ or 'CYGWIN' in os.environ:
                return str(path).replace('\\', '/')  # Unix-style paths
            else:
                return str(path).replace('/', '\\')  # Windows-style paths
        else:
            return str(path).replace('\\', '/')  # Unix-style paths

    @staticmethod
    def resolve_cwd(working_dir=None):
        """Get absolute path for cwd parameter."""
        if working_dir:
            return str(Path(working_dir).resolve())
        return None
```

### 6. Create Tests for Subprocess Execution

**File**: `tests/test_subprocess_cross_platform.py`

- Test git operations on Windows and Linux
- Test path handling with spaces and special characters
- Test shell vs non-shell execution
- Test timeout handling
- Test proper encoding

## Files to Create/Modify

### New Files
- `packages/csc-service/csc_service/shared/subprocess_helper.py` (200 lines)
- `packages/csc-service/csc_service/shared/path_helper.py` (150 lines)
- `tests/test_subprocess_cross_platform.py` (15 tests)

### Modified Files
- `packages/csc-service/csc_service/shared/services/agent_service.py` - Use SubprocessRunner in assign()
- `packages/csc-service/csc_service/shared/platform.py` - Add subprocess_config section
- `bin/csc-ctl` - Rewrite as Python using platform helpers

## Implementation Steps

1. **Debug agent assign segfault** - Add logging and find exact line causing segfault
2. **Create subprocess_helper.py** - Unified cross-platform subprocess wrapper
3. **Create path_helper.py** - Path normalization utilities
4. **Fix agent_service.py** - Use SubprocessRunner instead of raw subprocess.run()
5. **Update platform.py** - Add subprocess_config to platform.json
6. **Create tests** - Test subprocess on target platforms
7. **Verify on all platforms** - Test on Windows, Linux, macOS

## Acceptance Criteria

- ✓ agent assign works without segfault on Windows, Linux, macOS
- ✓ All paths loaded from platform.json (no hardcoded paths)
- ✓ Subprocess calls use platform-aware configuration
- ✓ Works with both native shells (cmd.exe, bash) and Git Bash
- ✓ Path handling works with spaces and special characters
- ✓ All 15 tests pass on Windows and Linux
- ✓ csc-ctl rewritten as Python, works everywhere
- ✓ No OS-specific code paths (all differences in platform.json)
- ✓ Future scripts can use SubprocessRunner for reliability

## Why This Matters

- **Reliability**: Proper subprocess handling prevents segfaults
- **Portability**: Same code works on all platforms
- **Maintainability**: Platform differences in one config file, not scattered code
- **Scalability**: New scripts just use the helpers, no reinventing subprocess handling
- **Debugging**: Centralized logging and error handling

PID: 31204 agent: opus starting at 2026-02-25 15:46:06

PID: 40884 agent: opus starting at 2026-02-25 15:46:06


--- AUDIT [2026-02-27 13:22] ---
INCOMPLETE
Pending:
  - Create subprocess_helper.py with SubprocessRunner class
  - Create path_helper.py with CrossPlatformPath utilities
  - Implement tests in test_subprocess_cross_platform.py with results
  - Modify agent_service.py assign() method to use SubprocessRunner
  - Update platform.py with subprocess_config section
  - Rewrite bin/csc-ctl as Python CLI
  - Debug and identify exact cause of agent assign segfault
  - Verify fix works on Windows, Linux, macOS with actual test execution
  - Document work log showing implementation steps taken
Planning document only - no actual implementation or testing performed, no work log recorded


DEAD END - Fix already applied in current codebase
