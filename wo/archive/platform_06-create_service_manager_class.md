# platform_06: Create ServiceManager Core Class

**Objective:** Create `ServiceManager` class that routes service install/uninstall to platform-specific handlers.

**Depends on:** platform_00-05
**Time:** ~45 minutes | **Difficulty:** Medium | **Next:** platform_07

---

## Task

Add `ServiceManager` class that:
1. Routes service operations to platform-specific implementation
2. Provides unified interface (install, uninstall, status, start, stop)
3. Uses detectors from platform_04 and platform_05
4. Returns status and error information

---

## File to Create

**`packages/csc-shared/csc_shared/platform_service_manager.py`**

Core service management class.

---

## Implementation

```python
"""Unified service management across platforms."""

from typing import Dict, Optional, Tuple
from abc import ABC, abstractmethod


class ServiceProvider(ABC):
    """Base class for platform-specific service providers."""

    @abstractmethod
    def install(self, service_name: str, config: Dict) -> Tuple[bool, str]:
        """Install service. Returns (success, message)."""
        pass

    @abstractmethod
    def uninstall(self, service_name: str) -> Tuple[bool, str]:
        """Uninstall service. Returns (success, message)."""
        pass

    @abstractmethod
    def start(self, service_name: str) -> Tuple[bool, str]:
        """Start service. Returns (success, message)."""
        pass

    @abstractmethod
    def stop(self, service_name: str) -> Tuple[bool, str]:
        """Stop service. Returns (success, message)."""
        pass

    @abstractmethod
    def status(self, service_name: str) -> Dict:
        """Get service status."""
        pass


class ServiceManager:
    """Manage services across all platforms."""

    def __init__(self, platform_data: Dict, command_builder=None):
        """Initialize with platform data.

        Args:
            platform_data: Platform detection data
            command_builder: CommandBuilder instance for generating commands
        """
        self.platform_data = platform_data
        self.os_type = platform_data.get("os")
        self.runtime = platform_data.get("runtime_strategy", {}).get("preferred")
        self.command_builder = command_builder
        self.provider = self._get_provider()

    def _get_provider(self) -> Optional[ServiceProvider]:
        """Get platform-specific service provider."""
        if self.os_type == "windows":
            from csc_shared.platform_service_windows import WindowsServiceProvider
            return WindowsServiceProvider(self.platform_data, self.command_builder)

        elif self.os_type in ["linux", "wsl"]:
            from csc_shared.platform_service_linux import LinuxServiceProvider
            return LinuxServiceProvider(self.platform_data, self.command_builder)

        else:
            return None

    def install(self, service_name: str, config: Dict) -> Tuple[bool, str]:
        """Install a service.

        Args:
            service_name: "server", "bridge", "queue-worker", etc.
            config: Service configuration dict

        Returns:
            (success: bool, message: str)
        """
        if not self.provider:
            return (False, f"No service provider for OS: {self.os_type}")

        return self.provider.install(service_name, config)

    def uninstall(self, service_name: str) -> Tuple[bool, str]:
        """Uninstall a service.

        Args:
            service_name: "server", "bridge", etc.

        Returns:
            (success: bool, message: str)
        """
        if not self.provider:
            return (False, f"No service provider for OS: {self.os_type}")

        return self.provider.uninstall(service_name)

    def start(self, service_name: str) -> Tuple[bool, str]:
        """Start a service."""
        if not self.provider:
            return (False, f"No service provider for OS: {self.os_type}")

        return self.provider.start(service_name)

    def stop(self, service_name: str) -> Tuple[bool, str]:
        """Stop a service."""
        if not self.provider:
            return (False, f"No service provider for OS: {self.os_type}")

        return self.provider.stop(service_name)

    def status(self, service_name: str) -> Dict:
        """Get service status."""
        if not self.provider:
            return {
                "exists": False,
                "running": False,
                "error": f"No service provider for OS: {self.os_type}"
            }

        return self.provider.status(service_name)

    def install_all(self, services: Dict) -> Dict[str, Tuple[bool, str]]:
        """Install multiple services.

        Args:
            services: Dict of service_name -> config

        Returns:
            Dict of service_name -> (success, message)
        """
        results = {}
        for service_name, config in services.items():
            results[service_name] = self.install(service_name, config)
        return results

    def uninstall_all(self, service_names: list) -> Dict[str, Tuple[bool, str]]:
        """Uninstall multiple services.

        Args:
            service_names: List of service names

        Returns:
            Dict of service_name -> (success, message)
        """
        results = {}
        for service_name in service_names:
            results[service_name] = self.uninstall(service_name)
        return results

    def status_all(self, service_names: list) -> Dict[str, Dict]:
        """Get status of multiple services."""
        results = {}
        for service_name in service_names:
            results[service_name] = self.status(service_name)
        return results

    def to_dict(self) -> dict:
        """Convert to dict."""
        return {
            "os_type": self.os_type,
            "runtime": self.runtime,
            "provider": type(self.provider).__name__ if self.provider else None
        }
```

---

## Integration with Platform Class

In `platform.py`, add method to `Platform` class:

```python
def get_service_manager(self) -> "ServiceManager":
    """Get service manager for this platform."""
    if not hasattr(self, '_service_manager'):
        from csc_shared.platform_service_manager import ServiceManager
        cb = self.get_command_builder()
        self._service_manager = ServiceManager(self.to_dict(), cb)

    return self._service_manager
```

---

## Testing

Create test script:

```python
from csc_shared.platform import Platform

p = Platform()
sm = p.get_service_manager()

print(f"Service Manager Info: {sm.to_dict()}")
print(f"Provider: {type(sm.provider).__name__ if sm.provider else 'None'}")

# Try to get status of non-existent service (should not error)
status = sm.status("server")
print(f"\nServer status: {status}")

# Show that manager is ready for install/uninstall
print(f"\nManager ready: {sm.provider is not None}")
```

---

## Verification Checklist

- [ ] `ServiceManager` class created in new file
- [ ] `_get_provider()` returns correct provider for platform
- [ ] `install()`, `uninstall()`, `start()`, `stop()` route to provider
- [ ] Batch methods (`install_all`, etc.) work
- [ ] `status()` returns dict (doesn't error on non-existent service)
- [ ] Platform.get_service_manager() returns instance
- [ ] Test script runs without errors
- [ ] Works on both Windows and Linux/WSL systems

---

## Commit

```
feat: Create ServiceManager for cross-platform service management

- Unified interface for all platforms
- Routes to Windows or Linux service provider
- Supports install, uninstall, start, stop, status operations
- Batch operations for multiple services
- Platform.get_service_manager() returns instance
```

