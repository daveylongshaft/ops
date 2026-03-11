# platform_09: Add csc-ctl service Commands

**Objective:** Add `service install/uninstall/start/stop/status` commands to csc-ctl CLI.

**Depends on:** platform_00-08
**Time:** ~45 minutes | **Difficulty:** Medium | **Next:** platform_10

---

## Task

Extend `csc-ctl` command handler to support:
- `csc-ctl service install all` - Install all services
- `csc-ctl service install server` - Install specific service
- `csc-ctl service uninstall server` - Uninstall service
- `csc-ctl service start server` - Start service
- `csc-ctl service stop server` - Stop service
- `csc-ctl service status` - Show all services
- `csc-ctl service status server` - Show specific service

---

## Files to Edit

**`packages/csc-service/csc_service/infra/ctl.py`** (or wherever csc-ctl commands are defined)

Or **`packages/csc-service/csc_service/main.py`** if ctl is in main.

Look for where commands like `csc-ctl status` are handled.

---

## Implementation

Add these methods to the csc-ctl command handler class:

```python
def cmd_service_install(self, args: list) -> int:
    """Install services: csc-ctl service install [all|service-name]."""
    from csc_shared.platform import Platform

    p = Platform()
    sm = p.get_service_manager()

    if not sm.provider:
        self.log("ERROR", f"No service manager available for {p.os_type}")
        return 1

    # Get service configs from platform
    services = p.to_dict().get("services", {})

    if not args:
        self.log("ERROR", "Usage: csc-ctl service install [all|service-name]")
        return 1

    target = args[0]

    if target == "all":
        # Install all enabled services
        self.log("INFO", "Installing all services...")
        results = sm.install_all({
            name: cfg for name, cfg in services.items()
            if cfg.get("enabled")
        })

        for service_name, (success, msg) in results.items():
            status = "[OK]" if success else "[FAIL]"
            self.log("INFO", f"{status} {service_name}: {msg}")

        return 0 if all(r[0] for r in results.values()) else 1
    else:
        # Install specific service
        config = services.get(target)
        if not config:
            self.log("ERROR", f"Unknown service: {target}")
            return 1

        success, msg = sm.install(target, config)
        status = "[OK]" if success else "[FAIL]"
        self.log("INFO", f"{status} {target}: {msg}")
        return 0 if success else 1

def cmd_service_uninstall(self, args: list) -> int:
    """Uninstall services: csc-ctl service uninstall [all|service-name]."""
    from csc_shared.platform import Platform

    p = Platform()
    sm = p.get_service_manager()

    if not sm.provider:
        self.log("ERROR", f"No service manager available for {p.os_type}")
        return 1

    if not args:
        self.log("ERROR", "Usage: csc-ctl service uninstall [all|service-name]")
        return 1

    target = args[0]

    if target == "all":
        # Uninstall all services
        self.log("INFO", "Uninstalling all services...")
        services = p.to_dict().get("services", {}).keys()
        results = sm.uninstall_all(list(services))

        for service_name, (success, msg) in results.items():
            status = "[OK]" if success else "[FAIL]"
            self.log("INFO", f"{status} {service_name}: {msg}")

        return 0 if all(r[0] for r in results.values()) else 1
    else:
        success, msg = sm.uninstall(target)
        status = "[OK]" if success else "[FAIL]"
        self.log("INFO", f"{status} {target}: {msg}")
        return 0 if success else 1

def cmd_service_start(self, args: list) -> int:
    """Start a service: csc-ctl service start <service-name>."""
    from csc_shared.platform import Platform

    p = Platform()
    sm = p.get_service_manager()

    if not args:
        self.log("ERROR", "Usage: csc-ctl service start <service-name>")
        return 1

    service_name = args[0]
    success, msg = sm.start(service_name)
    status = "[OK]" if success else "[FAIL]"
    self.log("INFO", f"{status} {service_name}: {msg}")
    return 0 if success else 1

def cmd_service_stop(self, args: list) -> int:
    """Stop a service: csc-ctl service stop <service-name>."""
    from csc_shared.platform import Platform

    p = Platform()
    sm = p.get_service_manager()

    if not args:
        self.log("ERROR", "Usage: csc-ctl service stop <service-name>")
        return 1

    service_name = args[0]
    success, msg = sm.stop(service_name)
    status = "[OK]" if success else "[FAIL]"
    self.log("INFO", f"{status} {service_name}: {msg}")
    return 0 if success else 1

def cmd_service_status(self, args: list) -> int:
    """Show service status: csc-ctl service status [service-name]."""
    from csc_shared.platform import Platform

    p = Platform()
    sm = p.get_service_manager()

    self.log("INFO", "Service Status Report")
    self.log("INFO", "=" * 60)

    if args:
        # Specific service
        service_name = args[0]
        status = sm.status(service_name)
        self._print_service_status(service_name, status)
    else:
        # All services
        services = p.to_dict().get("services", {})
        for service_name in services.keys():
            status = sm.status(service_name)
            self._print_service_status(service_name, status)

    return 0

def _print_service_status(self, service_name: str, status: dict):
    """Print status for one service."""
    if status.get("exists"):
        running = "✓ Running" if status.get("running") else "✗ Stopped"
        enabled = "(auto-start)" if status.get("enabled") else ""
        self.log("INFO", f"{service_name}: {running} {enabled}")
    else:
        self.log("INFO", f"{service_name}: Not installed")

def cmd_service(self, args: list) -> int:
    """Service management: csc-ctl service <operation> [target]."""
    if not args:
        self.log("ERROR", "Usage: csc-ctl service <install|uninstall|start|stop|status> [all|service-name]")
        return 1

    operation = args[0]
    operation_args = args[1:] if len(args) > 1 else []

    if operation == "install":
        return self.cmd_service_install(operation_args)
    elif operation == "uninstall":
        return self.cmd_service_uninstall(operation_args)
    elif operation == "start":
        return self.cmd_service_start(operation_args)
    elif operation == "stop":
        return self.cmd_service_stop(operation_args)
    elif operation == "status":
        return self.cmd_service_status(operation_args)
    else:
        self.log("ERROR", f"Unknown operation: {operation}")
        return 1
```

---

## Integration with Main Command Router

Find the main command dispatcher (typically in `main()` or a command handler class) and add:

```python
elif cmd == "service":
    return self.cmd_service(args)
```

---

## Testing Commands

After implementation, test with:

```bash
# Show current status
csc-ctl service status

# Show specific service
csc-ctl service status server

# Install all services (may require sudo on Linux)
csc-ctl service install all

# Install specific
csc-ctl service install server

# Start/stop
csc-ctl service start server
csc-ctl service stop server

# Uninstall
csc-ctl service uninstall server
```

---

## Verification Checklist

- [ ] `cmd_service()` main handler added to csc-ctl
- [ ] `cmd_service_install()` installs single/all services
- [ ] `cmd_service_uninstall()` uninstalls services
- [ ] `cmd_service_start()` starts service
- [ ] `cmd_service_stop()` stops service
- [ ] `cmd_service_status()` shows status
- [ ] `_print_service_status()` formats output nicely
- [ ] Main command router calls `cmd_service()`
- [ ] All commands work without errors (test on your platform)
- [ ] Handles missing arguments gracefully (shows usage)

---

## Commit

```
feat: Add csc-ctl service management commands

- service install [all|service-name] - Install services
- service uninstall [all|service-name] - Remove services
- service start <service-name> - Start service
- service stop <service-name> - Stop service
- service status [service-name] - Show status
- Uses ServiceManager from platform detection
- Cross-platform: Windows (NSSM), Linux (systemd)
```

