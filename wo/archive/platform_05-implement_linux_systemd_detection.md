# platform_05: Implement Linux/systemd Service Detection

**Objective:** Detect systemd services on Linux and WSL.

**Depends on:** platform_00, platform_01, platform_02, platform_03
**Time:** ~40 minutes | **Difficulty:** Medium | **Next:** platform_06

---

## Task

Add `LinuxServiceDetector` class that:
1. Lists systemd units matching "csc-*" pattern
2. Checks service status (active, inactive, failed)
3. Gets service details (enabled, user, etc.)
4. Works on Linux/Debian and WSL

---

## File to Create

**`packages/csc-shared/csc_shared/platform_service_linux.py`**

New file for Linux/systemd-specific service detection.

---

## Implementation

```python
"""Linux/systemd service detection and management."""

import subprocess
from typing import List, Dict, Optional


class LinuxServiceDetector:
    """Detect systemd services related to CSC."""

    SERVICE_PREFIX = "csc-"

    @staticmethod
    def list_services() -> List[Dict]:
        """List all CSC-related systemd services.

        Returns:
            List of dicts with service info (name, status, enabled, etc.)
        """
        try:
            # Use systemctl to list services
            cmd = [
                "systemctl",
                "list-units",
                f"--all",
                f"--pattern={LinuxServiceDetector.SERVICE_PREFIX}*",
                "--output=json"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                return []

            import json
            try:
                data = json.loads(result.stdout)
                return data if isinstance(data, list) else []
            except json.JSONDecodeError:
                return []
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return []

    @staticmethod
    def get_service_status(service_name: str) -> Optional[Dict]:
        """Get status of specific service.

        Args:
            service_name: Service name (e.g., "csc-server", "csc-bridge")

        Returns:
            Dict with status info, or None if not found
        """
        try:
            # Add .service suffix if not present
            if not service_name.endswith(".service"):
                service_name = f"{service_name}.service"

            cmd = ["systemctl", "show", service_name, "--output=json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                return None

            import json
            return json.loads(result.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError, Exception):
            return None

    @staticmethod
    def service_exists(service_name: str) -> bool:
        """Check if service exists."""
        status = LinuxServiceDetector.get_service_status(service_name)
        return status is not None and status.get("LoadState") != "not-found"

    @staticmethod
    def is_service_running(service_name: str) -> bool:
        """Check if service is currently running."""
        status = LinuxServiceDetector.get_service_status(service_name)
        if not status:
            return False
        return status.get("ActiveState") == "active"

    @staticmethod
    def is_service_enabled(service_name: str) -> bool:
        """Check if service is enabled (auto-start on boot)."""
        status = LinuxServiceDetector.get_service_status(service_name)
        if not status:
            return False
        enabled_state = status.get("UnitFileState")
        return enabled_state == "enabled"

    @staticmethod
    def to_dict() -> dict:
        """Get all services as dict."""
        services = LinuxServiceDetector.list_services()
        return {
            "services": services,
            "detected": len(services)
        }
```

---

## Integration with Platform Class

In `platform.py`, add method to `Platform` class:

```python
def get_linux_service_detector(self) -> "LinuxServiceDetector":
    """Get Linux service detector."""
    if self.platform_data.get("os") not in ["linux", "wsl"]:
        return None

    if not hasattr(self, '_linux_service_detector'):
        from csc_shared.platform_service_linux import LinuxServiceDetector
        self._linux_service_detector = LinuxServiceDetector()

    return self._linux_service_detector
```

---

## Testing

Create test script:

```python
from csc_shared.platform import Platform

p = Platform()

# Only works on Linux/WSL
if p.platform_data.get("os") not in ["linux", "wsl"]:
    print("Not on Linux/WSL, skipping test")
    exit(0)

detector = p.get_linux_service_detector()

# List all CSC services
print("CSC Services:")
services = detector.list_services()
if services:
    for svc in services:
        print(f"  - {svc['unit']}: {svc['active']}")
else:
    print("  (None installed yet)")

# Check specific service
if detector.service_exists("csc-server"):
    status = detector.get_service_status("csc-server")
    print(f"\ncsc-server status: {status.get('ActiveState')}")
    print(f"Running: {detector.is_service_running('csc-server')}")
    print(f"Enabled: {detector.is_service_enabled('csc-server')}")
else:
    print("\ncsc-server not installed")
```

---

## Verification Checklist

- [ ] `LinuxServiceDetector` class created in new file
- [ ] `list_services()` returns list of csc-* services
- [ ] `get_service_status()` retrieves service details
- [ ] `service_exists()`, `is_service_running()`, `is_service_enabled()` work
- [ ] Platform.get_linux_service_detector() returns instance (or None on non-Linux)
- [ ] Test script runs without errors on Linux/WSL
- [ ] Returns empty list if no CSC services installed (doesn't error)
- [ ] Handles .service suffix correctly

---

## Commit

```
feat: Add Linux/systemd service detection

- Detect csc-* services via systemctl list-units/show
- Check service status (active/inactive), enabled state
- Platform.get_linux_service_detector() for Linux/WSL systems
- Test output: [show services on your system or "None installed"]
```

