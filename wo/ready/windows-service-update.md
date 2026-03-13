PLATFORM: windows
AGENT: haiku
PRIORITY: normal

## Task: Stop, Update, Reinstall, and Restart CSC Services on Windows

You are running on Windows. Use csc-platform to resolve all paths — never hardcode
paths like C:\csc or /opt/csc.

### Step 1 — Resolve project root

```bat
for /f "tokens=*" %%i in ('csc-platform get_root') do set CSC_ROOT=%%i
for /f "tokens=*" %%i in ('csc-platform get_etc_dir') do set CSC_ETC=%%i
```

Or in Python:
```python
from csc_service.shared.platform import Platform
root = str(Platform.PROJECT_ROOT)
etc  = str(Platform.get_etc_dir())
```

### Step 2 — Stop and uninstall all CSC services

```bat
csc-ctl remove all
```

Verify each service is stopped and removed before continuing.
If any service fails to stop, force it:
```bat
csc-ctl remove all --force
```

### Step 3 — Pull latest irc submodule

```bat
cd %CSC_ROOT%\irc
git pull
```

### Step 4 — Reinstall the package

```bat
pip install -e %CSC_ROOT%\irc\packages\csc-service
```

### Step 5 — Install and start services

```bat
csc-ctl install all
csc-ctl start all
```

Verify services are running:
```bat
csc-ctl status
```

All listed services should show as active/running before continuing.

### Step 6 — Pull csc parent repo

```bat
cd %CSC_ROOT%
git pull
```

### Step 7 — Complete

Move this WO to done/ and commit + push the ops repo:

```bat
cd %CSC_ROOT%\ops
git add wo\
git commit -m "done: windows-service-update"
git push
```

### Success criteria

- `csc-ctl status` shows all services running
- No errors in `csc-platform get_etc_dir` output
- ops repo pushed with WO in done/

### Notes

- Use Platform for all path resolution — never hardcode drive letters or Unix paths
- If csc-ctl is not on PATH, run: `python -m csc_service.cli.main <command>`
- If NSSM is needed for service install, it is at: `%CSC_ROOT%\bin\nssm.exe`
- On failure at any step: stop, document the error at the bottom of this file, move to done/ anyway, and push so the failure is visible

## Log of Efforts - 2026-03-11

- **Initial Status**: csc-ctl on Windows was unable to start services because it lacked a native Windows provider.
- **NSSM Support**: Created irc/packages/csc-service/csc_service/shared/platform_service_windows.py with WindowsServiceProvider and WindowsServiceDetector to manage services as native Windows background tasks.
- **csc-ctl Enhancement**: Modified service_cmd.py to use WindowsServiceProvider for install/start/stop. This enables automated service registration.
- **Unified Launcher**: Built in/csc-service to provide a single entry point for the daemon, solving ModuleNotFoundError by managing sys.path.
- **Import Migration**:
    - Fixed csc_server import path in main.py.
    - Added enable_bridge support to the daemon loop.
    - Converted absolute imports to relative in server.py.
- **Environment**: Regenerated platform.json to fix path mismatch (Linux defaults on Windows host).
- **Current Blocker**: Service installation requires Administrator privileges, which cannot be obtained from the current non-elevated shell.
