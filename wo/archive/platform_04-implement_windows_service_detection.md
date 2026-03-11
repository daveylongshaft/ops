# platform_04: Implement Windows Service Detection

**Objective:** Detect if a Windows Service is installed and its current status (running, stopped, etc.).

**Depends on:** platform_00, platform_01, platform_02, platform_03
**Time:** ~40 minutes | **Difficulty:** Medium | **Next:** platform_05

---

## Task

Add `WindowsServiceDetector` class that:
1. Lists installed services matching "CSC-*" pattern
2. Checks service status (running, stopped, disabled)
3. Gets service details (startup type, executable path, etc.)
4. Works via Windows command-line tools (`sc` or `Get-Service`)

---

## File to Create

**`packages/csc-shared/csc_shared/platform_service_windows.py`**

New file for Windows-specific service detection.

---

## Implementation

```python
"""Windows service detection and management."""

import subprocess
import re
from typing import List, Dict, Optional


class WindowsServiceDetector:
    """Detect Windows services related to CSC."""

    SERVICE_PREFIX = "CSC-"

    @staticmethod
    def list_services() -> List[Dict]:
        """List all CSC-related Windows services.

        Returns:
            List of dicts with service info (name, status, startup_type, etc.)
        """
        try:
            # Use PowerShell to list services
            cmd = [
                "powershell",
                "-Command",
                f"Get-Service -Name '{WindowsServiceDetector.SERVICE_PREFIX}*' | "
                "Select-Object Name, Status, StartType | ConvertTo-Json"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                return []

            # Parse JSON output
            import json
            try:
                data = json.loads(result.stdout)
                # Ensure we have a list
                if isinstance(data, dict):
                    data = [data]
                return data if isinstance(data, list) else []
            except json.JSONDecodeError:
                return []
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return []

    @staticmethod
    def get_service_status(service_name: str) -> Optional[Dict]:
        """Get status of specific service.

        Args:
            service_name: Service name (e.g., "CSC-Server", "CSC-Bridge")

        Returns:
            Dict with status info, or None if not found
        """
        try:
            cmd = [
                "powershell",
                "-Command",
                f"Get-Service -Name '{service_name}' | "
                "Select-Object Name, Status, StartType, DisplayName | ConvertTo-Json"
            ]
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
        status = WindowsServiceDetector.get_service_status(service_name)
        return status is not None

    @staticmethod
    def is_service_running(service_name: str) -> bool:
        """Check if service is currently running."""
        status = WindowsServiceDetector.get_service_status(service_name)
        if not status:
            return False
        return status.get("Status") == "Running"

    @staticmethod
    def to_dict(self) -> dict:
        """Get all services as dict."""
        return {
            "services": self.list_services(),
            "detected": len(self.list_services())
        }
```

---

## Integration with Platform Class

In `platform.py`, add method to `Platform` class:

```python
def get_windows_service_detector(self) -> "WindowsServiceDetector":
    """Get Windows service detector."""
    if self.platform_data.get("os") != "windows":
        return None

    if not hasattr(self, '_windows_service_detector'):
        from csc_shared.platform_service_windows import WindowsServiceDetector
        self._windows_service_detector = WindowsServiceDetector()

    return self._windows_service_detector
```

---

## Testing

Create test script:

```python
from csc_shared.platform import Platform

p = Platform()

# Only works on Windows
if p.platform_data.get("os") != "windows":
    print("Not on Windows, skipping test")
    exit(0)

detector = p.get_windows_service_detector()

# List all CSC services
print("CSC Services:")
services = detector.list_services()
for svc in services:
    print(f"  - {svc}")

# Check specific service
if detector.service_exists("CSC-Server"):
    status = detector.get_service_status("CSC-Server")
    print(f"\nCSC-Server status: {status}")
    print(f"Running: {detector.is_service_running('CSC-Server')}")
else:
    print("\nCSC-Server not installed")
```

---

## Verification Checklist

- [ ] `WindowsServiceDetector` class created in new file
- [ ] `list_services()` returns list of CSC-* services
- [ ] `get_service_status()` retrieves service details
- [ ] `service_exists()` and `is_service_running()` work
- [ ] Platform.get_windows_service_detector() returns instance (or None on non-Windows)
- [ ] Test script runs without errors on Windows
- [ ] Returns empty list if no CSC services installed (doesn't error)

---

## Commit

```
feat: Add Windows service detection

- Detect CSC-* services via PowerShell Get-Service
- Check service status (Running/Stopped), startup type
- Platform.get_windows_service_detector() for Windows systems
- Test output: [show services on your Windows system or "None installed"]
```

