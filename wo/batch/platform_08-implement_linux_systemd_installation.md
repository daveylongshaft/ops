# platform_08: Implement Linux/systemd Service Installation

**Objective:** Implement systemd service installation for Linux and WSL.

**Depends on:** platform_05, platform_06
**Time:** ~50 minutes | **Difficulty:** Medium | **Next:** platform_09

---

## Task

Add `LinuxServiceProvider` class that:
1. Creates systemd unit files
2. Enables/disables services
3. Manages service start/stop
4. Works on Linux and WSL

---

## File to Edit

**`packages/csc-shared/csc_shared/platform_service_linux.py`**

Extend the existing file (from platform_05) to add `LinuxServiceProvider`.

---

## systemd Unit File Format

Systemd unit files go in `/etc/systemd/system/` (requires sudo).

Example for csc-server.service:
```ini
[Unit]
Description=CSC Server - IRC Protocol Server
After=network.target
Wants=csc-bridge.service

[Service]
Type=simple
User=davey
WorkingDirectory=/opt/csc
ExecStart=/usr/bin/python3 -m csc_service.server.main
Restart=always
RestartSec=10
StandardOutput=append:/var/log/csc/csc-server.log
StandardError=append:/var/log/csc/csc-server.log
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

---

## Implementation

Add to `platform_service_linux.py`:

```python
import subprocess
from pathlib import Path
from typing import Tuple, Optional
import os


class LinuxServiceProvider:
    """Install/manage services on Linux/WSL using systemd."""

    SYSTEMD_DIR = Path("/etc/systemd/system")
    LOG_DIR = Path("/var/log/csc")

    def __init__(self, platform_data: dict, command_builder=None):
        """Initialize Linux service provider."""
        self.platform_data = platform_data
        self.command_builder = command_builder
        self._ensure_log_dir()

    def _ensure_log_dir(self):
        """Ensure log directory exists."""
        try:
            if not self.LOG_DIR.exists():
                # This might need sudo, but attempt anyway
                subprocess.run(
                    ["sudo", "mkdir", "-p", str(self.LOG_DIR)],
                    capture_output=True,
                    timeout=10
                )
                subprocess.run(
                    ["sudo", "chmod", "755", str(self.LOG_DIR)],
                    capture_output=True,
                    timeout=10
                )
        except Exception:
            pass  # Continue if log dir creation fails

    def _generate_unit_file(self, service_name: str, config: dict) -> str:
        """Generate systemd unit file content.

        Args:
            service_name: "server", "bridge", etc.
            config: Service config dict

        Returns:
            systemd unit file content (string)
        """
        module = config.get("module", "")
        log_file = config.get("log_file", f"/var/log/csc/{service_name}.log")
        restart_sec = 10 if config.get("auto_restart") else 0

        # Get user (default to current user)
        user = os.environ.get("USER", "davey")

        # Nice description
        description = {
            "server": "CSC Server - IRC Protocol Server",
            "bridge": "CSC Bridge - Protocol Bridge Proxy",
            "queue-worker": "CSC Queue Worker - Workorder Processing",
            "pm": "CSC PM - Project Manager",
            "client": "CSC Client - Interactive CLI"
        }.get(service_name, f"CSC {service_name.title()}")

        # Build unit file
        unit_file = f"""[Unit]
Description={description}
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={Path.home() / ".csc"}
ExecStart=/usr/bin/python3 -m {module}
Restart=always
RestartSec={restart_sec}
StandardOutput=append:{log_file}
StandardError=append:{log_file}
Environment="PYTHONUNBUFFERED=1"
Environment="PYTHONDONTWRITEBYTECODE=1"

[Install]
WantedBy=multi-user.target
"""
        return unit_file

    def install(self, service_name: str, config: dict) -> Tuple[bool, str]:
        """Install a service using systemd.

        Args:
            service_name: "server", "bridge", etc.
            config: Service config dict

        Returns:
            (success, message)
        """
        if not config.get("module"):
            return (False, "No module specified in config")

        unit_name = f"csc-{service_name}.service"
        unit_path = self.SYSTEMD_DIR / unit_name

        # Check if already installed
        if unit_path.exists():
            return (False, f"Service {unit_name} already installed")

        try:
            # Generate unit file
            unit_content = self._generate_unit_file(service_name, config)

            # Write unit file (requires sudo)
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.service', delete=False) as f:
                f.write(unit_content)
                temp_path = f.name

            # Copy to systemd dir with sudo
            result = subprocess.run(
                ["sudo", "cp", temp_path, str(unit_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            os.unlink(temp_path)

            if result.returncode != 0:
                return (False, f"Failed to copy unit file: {result.stderr}")

            # Set permissions
            subprocess.run(
                ["sudo", "chmod", "644", str(unit_path)],
                capture_output=True,
                timeout=10
            )

            # Reload systemd daemon
            subprocess.run(
                ["sudo", "systemctl", "daemon-reload"],
                capture_output=True,
                timeout=10
            )

            # Enable service if configured
            if config.get("auto_start"):
                enable_result = subprocess.run(
                    ["sudo", "systemctl", "enable", unit_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if enable_result.returncode != 0:
                    print(f"[WARN] Failed to enable {unit_name}: {enable_result.stderr}")

            return (True, f"Service {unit_name} installed and enabled")

        except subprocess.TimeoutExpired:
            return (False, f"Timeout installing {unit_name}")
        except Exception as e:
            return (False, f"Error installing service: {str(e)}")

    def uninstall(self, service_name: str) -> Tuple[bool, str]:
        """Uninstall a service."""
        unit_name = f"csc-{service_name}.service"
        unit_path = self.SYSTEMD_DIR / unit_name

        if not unit_path.exists():
            return (False, f"Service {unit_name} not installed")

        try:
            # Stop the service first
            subprocess.run(
                ["sudo", "systemctl", "stop", unit_name],
                capture_output=True,
                timeout=10
            )

            # Disable
            subprocess.run(
                ["sudo", "systemctl", "disable", unit_name],
                capture_output=True,
                timeout=10
            )

            # Remove unit file
            result = subprocess.run(
                ["sudo", "rm", str(unit_path)],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return (False, f"Failed to remove unit file: {result.stderr}")

            # Reload systemd
            subprocess.run(
                ["sudo", "systemctl", "daemon-reload"],
                capture_output=True,
                timeout=10
            )

            return (True, f"Service {unit_name} uninstalled")

        except Exception as e:
            return (False, f"Error uninstalling service: {str(e)}")

    def start(self, service_name: str) -> Tuple[bool, str]:
        """Start a service."""
        unit_name = f"csc-{service_name}.service"

        try:
            result = subprocess.run(
                ["sudo", "systemctl", "start", unit_name],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return (False, f"Failed to start {unit_name}: {result.stderr}")

            return (True, f"Service {unit_name} started")

        except Exception as e:
            return (False, f"Error starting service: {str(e)}")

    def stop(self, service_name: str) -> Tuple[bool, str]:
        """Stop a service."""
        unit_name = f"csc-{service_name}.service"

        try:
            result = subprocess.run(
                ["sudo", "systemctl", "stop", unit_name],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return (False, f"Failed to stop {unit_name}: {result.stderr}")

            return (True, f"Service {unit_name} stopped")

        except Exception as e:
            return (False, f"Error stopping service: {str(e)}")

    def status(self, service_name: str) -> dict:
        """Get service status."""
        unit_name = f"csc-{service_name}.service"
        detector_status = LinuxServiceDetector.get_service_status(unit_name)

        if detector_status:
            return {
                "exists": True,
                "running": detector_status.get("ActiveState") == "active",
                "name": unit_name,
                "status": detector_status.get("ActiveState"),
                "enabled": detector_status.get("UnitFileState") == "enabled"
            }
        else:
            return {
                "exists": False,
                "running": False,
                "name": unit_name
            }
```

---

## Verification Checklist

- [ ] `LinuxServiceProvider` class created
- [ ] `_generate_unit_file()` produces valid systemd unit files
- [ ] `install()` creates unit file and enables service (with sudo)
- [ ] `uninstall()` removes unit file and disables service
- [ ] `start()` and `stop()` work
- [ ] `status()` returns correct info
- [ ] Test on Linux/WSL system (may need sudo)
- [ ] Unit files created in /etc/systemd/system/csc-*.service

---

## Commit

```
feat: Implement Linux/systemd service installation

- Generate valid systemd unit files per service
- Install units to /etc/systemd/system/ (requires sudo)
- Enable services for auto-start on boot
- Support service start/stop/uninstall operations
- LinuxServiceProvider implements ServiceProvider interface
- Works on Linux, Debian, WSL
```

