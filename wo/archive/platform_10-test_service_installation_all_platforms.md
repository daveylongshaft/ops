# platform_10: Test Service Installation Across All Platforms

**Objective:** Verify service installation/management works correctly on Windows, Linux, and WSL.

**Depends on:** platform_00-09
**Time:** ~60 minutes | **Difficulty:** Medium | **Next:** Done

---

## Task

Test the complete service installation and management flow:
1. Run platform detection
2. Verify service manager works
3. Test install/uninstall cycle for at least one service
4. Verify service starts/stops correctly
5. Document results

---

## Test Plan by Platform

### Test on Your Current System

Run these checks in order:

#### Step 1: Platform Detection

```python
from csc_shared.platform import Platform

p = Platform()
print(f"OS: {p.platform_data.get('os')}")
print(f"Runtime Strategy: {p.get_runtime_strategy().to_dict()}")
print(f"Preferred Runtime: {p.get_runtime_strategy().preferred}")
print(f"Available: {p.get_runtime_strategy().available}")
```

Expected: Shows your OS, detected runtimes, etc.

#### Step 2: Service Manager

```python
sm = p.get_service_manager()
print(f"Service Provider: {type(sm.provider).__name__}")
print(f"Provider Ready: {sm.provider is not None}")
```

Expected: Shows Windows/Linux service provider.

#### Step 3: Try to Install a Test Service

```bash
# Try to install server service
csc-ctl service install server
```

Expected:
- **Windows**: Service CSC-Server installed (or NSSM auto-downloaded)
- **Linux/WSL**: Unit file created, requires sudo password

#### Step 4: Check Status

```bash
csc-ctl service status server
```

Expected: Shows "Not installed" or "Stopped" (if installed)

#### Step 5: Try to Uninstall

```bash
csc-ctl service uninstall server
```

Expected: Service removed without errors.

---

## What to Test (Checklist)

- [ ] Platform detection works on your system
- [ ] Correct runtime detected (native, WSL, or Docker)
- [ ] Service manager initializes without errors
- [ ] Correct service provider loaded (Windows vs Linux)
- [ ] Can list available services with `csc-ctl service status`
- [ ] Can install a service (test with "server")
- [ ] Can uninstall a service
- [ ] Can check status of installed service
- [ ] NSSM downloads on Windows (if not already installed)
- [ ] systemd units created on Linux/WSL (check `/etc/systemd/system/csc-*.service`)
- [ ] Starting/stopping service works (if installed)

---

## Troubleshooting

### On Windows

**NSSM Download Issues:**
- Check internet connection
- If NSSM fails to download, manually download from https://nssm.cc/download and extract to C:\csc\bin\

**Service Already Exists:**
- Use `Get-Service -Name CSC-Server` to check
- Remove with: `nssm remove CSC-Server confirm`

**Requires Admin:**
- You may need to open cmd as Administrator for NSSM commands to work

### On Linux/WSL

**Permission Denied:**
- systemd install requires `sudo`
- You'll be prompted for password when running `csc-ctl service install`

**systemd not Available:**
- WSL 1 doesn't have systemd; need WSL 2
- Check: `wsl --version` (should show version 2+)

**Port Already in Use:**
- Old CSC processes still running
- Kill with: `pkill -f csc-server`

---

## Test Results Template

Document your test run in the commit:

```
Platform: [Windows/Linux/WSL]
OS: [Windows 10/Ubuntu 22.04/etc]
Runtime: [native/wsl/docker]
Service Provider: [Windows/Linux]

✓ Platform detection works
✓ Service manager initializes
✓ Can list services
✓ Can install server service
✓ Service shows in status output
✓ Can uninstall service
? [Any issues encountered]

Notes:
- [Any special setup needed]
- [Any quirks or gotchas]
```

---

## Verification Checklist

- [ ] Tests run on your current system
- [ ] Platform detection correct
- [ ] Service manager loads correct provider
- [ ] No Python errors in any operation
- [ ] Service commands work (install/uninstall)
- [ ] Status output is readable
- [ ] Document results in commit message
- [ ] Note platform/OS/runtime in commit

---

## Commit

```
test: Verify service installation on [platform]

Tested:
- Platform detection ✓
- Service manager initialization ✓
- Service install/uninstall ✓
- Service status output ✓
- NSSM (Windows) / systemd (Linux/WSL) ✓

Platform: [Your platform]
OS: [Your OS]
Runtime: [Detected runtime]
Issues: [None / list any found]

Notes: [Any special observations]
```

---

## If Tests Fail

Create a workorder documenting:
1. What failed
2. Error message (full traceback)
3. Platform info (OS, Python version, etc.)
4. What was attempted

This helps the next agent fix the issue.

