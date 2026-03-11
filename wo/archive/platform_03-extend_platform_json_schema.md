# platform_03: Extend platform.json Schema with Service Config

**Objective:** Update platform.json schema to include runtime strategy, path mappings, and service configuration.

**Depends on:** platform_00, platform_01, platform_02
**Time:** ~30 minutes | **Difficulty:** Easy | **Next:** platform_04

---

## Task

Extend `platform.json` schema to include:
1. Runtime strategy (available, preferred)
2. Path mappings (translated paths for each runtime)
3. Service configuration (per-service settings)
4. Bootstrap status (first-run configuration done?)

---

## File Context

**Current platform.json** (in `packages/csc-service/csc_service/server/` or service root):

Currently stores: `platform`, `hardware`, `os_details`, `virtualization`, etc.

**Update to add:**
- `runtime_strategy` section
- `paths` section with translated paths
- `services` section with per-service config
- `bootstrap_status` section

---

## Updated Schema

Here's what the new `platform.json` should look like:

```json
{
  "timestamp": "2026-02-28T18:45:30Z",
  "platform": { "os": "windows", ... },
  "hardware": { ... },
  "virtualization": { ... },

  "runtime_strategy": {
    "available": ["native", "wsl", "docker"],
    "preferred": "wsl",
    "config": {
      "native": {
        "python_path": "C:\\Python312\\python.exe",
        "python_version": "3.12.3",
        "type": "native"
      },
      "wsl": {
        "distro": "Ubuntu",
        "python_path": "/usr/bin/python3",
        "type": "wsl"
      },
      "docker": {
        "runtime": "docker",
        "type": "docker"
      }
    }
  },

  "paths": {
    "runtime_type": "wsl",
    "base_paths": {
      "native": "C:\\csc",
      "wsl": "/mnt/c/csc",
      "docker": "/app/csc",
      "linux": "/opt/csc",
      "macos": "/opt/csc"
    },
    "csc_root": "/mnt/c/csc",
    "packages": "/mnt/c/csc/packages",
    "pythonpath": "/mnt/c/csc/packages/csc-service:/mnt/c/csc/packages/csc-shared",
    "logs": "/tmp",
    "data": "/mnt/c/csc/packages/csc-service/csc_service/server"
  },

  "services": {
    "server": {
      "enabled": true,
      "runtime": "wsl",
      "module": "csc_service.server.main",
      "listen_host": "0.0.0.0",
      "listen_port": 9525,
      "protocol": "udp",
      "log_file": "/tmp/csc-server.log",
      "install_method": "systemd",
      "auto_start": true
    },
    "bridge": {
      "enabled": true,
      "runtime": "wsl",
      "module": "csc_service.bridge.main",
      "listen_host": "0.0.0.0",
      "listen_port": 9667,
      "protocol": "tcp",
      "log_file": "/tmp/csc-bridge.log",
      "install_method": "systemd",
      "auto_start": true
    },
    "queue-worker": {
      "enabled": true,
      "runtime": "wsl",
      "module": "csc_service.infra.queue_worker",
      "poll_interval": 60,
      "log_file": "/tmp/csc-queue-worker.log",
      "install_method": "systemd",
      "auto_start": false
    },
    "client": {
      "enabled": false,
      "runtime": "wsl",
      "module": "csc_service.client.main",
      "interactive": true,
      "install_method": "none",
      "auto_start": false
    },
    "pm": {
      "enabled": true,
      "runtime": "wsl",
      "module": "csc_service.infra.pm",
      "poll_interval": 30,
      "log_file": "/tmp/csc-pm.log",
      "install_method": "systemd",
      "auto_start": false
    }
  },

  "bootstrap_status": {
    "initialized": true,
    "first_run": false,
    "last_check": "2026-02-28T18:45:30Z",
    "checks_completed": {
      "runtime_detection": true,
      "path_translation": true,
      "python_import": true,
      "ports_available": false,
      "service_installation": false
    }
  }
}
```

---

## Implementation Steps

1. **Locate platform.json** - Find where it's currently saved
   - Likely in: `packages/csc-service/csc_service/server/platform.json`
   - Or passed via environment: `CSC_PLATFORM_FILE`

2. **Update the write method** in platform.py's `to_dict()`:
   - Already includes runtime_strategy (from platform_00)
   - Add paths section (from platform_01)
   - Add services section (skeleton - will be populated by ServiceManager later)
   - Add bootstrap_status section

3. **Add to Platform.to_dict()**:

```python
def to_dict(self) -> dict:
    data = {
        "timestamp": datetime.now().isoformat() + "Z",
        # ... existing code ...
        "runtime_strategy": self.get_runtime_strategy().to_dict(),
        "paths": self.get_path_translator().to_dict(),
        "command_builder": self.get_command_builder().to_dict(),
        "services": self._get_default_services(),
        "bootstrap_status": self._get_bootstrap_status()
    }
    return data

def _get_default_services(self) -> dict:
    """Return default service configuration."""
    return {
        "server": {
            "enabled": True,
            "runtime": self.get_runtime_strategy().preferred,
            "module": "csc_service.server.main",
            "listen_host": "0.0.0.0",
            "listen_port": 9525,
            "protocol": "udp",
            "auto_start": True
        },
        "bridge": {
            "enabled": True,
            "runtime": self.get_runtime_strategy().preferred,
            "module": "csc_service.bridge.main",
            "listen_host": "0.0.0.0",
            "listen_port": 9667,
            "protocol": "tcp",
            "auto_start": True
        },
        "queue-worker": {
            "enabled": True,
            "runtime": self.get_runtime_strategy().preferred,
            "module": "csc_service.infra.queue_worker",
            "poll_interval": 60,
            "auto_start": False
        },
        "pm": {
            "enabled": True,
            "runtime": self.get_runtime_strategy().preferred,
            "module": "csc_service.infra.pm",
            "poll_interval": 30,
            "auto_start": False
        }
    }

def _get_bootstrap_status(self) -> dict:
    """Return bootstrap status."""
    return {
        "initialized": True,
        "first_run": False,
        "last_check": datetime.now().isoformat() + "Z",
        "checks_completed": {
            "runtime_detection": True,
            "path_translation": True,
            "python_import": True,
            "ports_available": False,
            "service_installation": False
        }
    }
```

---

## Verification Checklist

- [ ] Updated `Platform.to_dict()` to include all new sections
- [ ] `_get_default_services()` returns proper config dict
- [ ] `_get_bootstrap_status()` returns proper status dict
- [ ] Platform object saves to JSON with new schema
- [ ] Can load platform.json and access new sections (runtime_strategy, paths, services, bootstrap_status)
- [ ] Import datetime if needed (`from datetime import datetime`)

---

## Commit

```
feat: Extend platform.json schema with runtime, paths, and service config

- Add runtime_strategy section (available/preferred runtimes)
- Add paths section (base paths for each runtime)
- Add services section (per-service configuration)
- Add bootstrap_status section (first-run checks)
- Platform.to_dict() includes all new sections
```

