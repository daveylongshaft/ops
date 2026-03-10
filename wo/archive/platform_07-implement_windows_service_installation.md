# platform_07: Implement Windows Service Installation (NSSM)

**Objective:** Implement Windows service installation using NSSM (Non-Sucking Service Manager).

**Depends on:** platform_04, platform_06
**Time:** ~50 minutes | **Difficulty:** Medium | **Next:** platform_08

---

## Task

Add `WindowsServiceProvider` class that:
1. Checks if NSSM is installed (download if needed)
2. Installs services using NSSM
3. Uninstalls services
4. Manages service start/stop/status

---

## File to Edit

**`packages/csc-shared/csc_shared/platform_service_windows.py`**

Extend the existing file (from platform_04) to add `WindowsServiceProvider`.

---

## NSSM Background

NSSM is a utility that runs any executable as a Windows Service.

**Download:** https://nssm.cc/download
**Installation:** Extract to a directory on PATH or to CSC's bin/ directory

Commands:
```
nssm install <service-name> <exe-path> [arguments]
nssm remove <service-name>
nssm start <service-name>
nssm stop <service-name>
nssm status <service-name>
```

---

## Implementation

Add to `platform_service_windows.py`:

```python
import os
import sys
from pathlib import Path


class WindowsServiceProvider:
    """Install/manage services on Windows using NSSM."""

    NSSM_URL = "https://nssm.cc/download/nssm-2.24-101-g897c7ad.zip"
    NSSM_VERSION = "2.24"

    def __init__(self, platform_data: dict, command_builder=None):
        """Initialize Windows service provider."""
        self.platform_data = platform_data
        self.command_builder = command_builder
        self.nssm_path = self._find_or_install_nssm()

    def _find_or_install_nssm(self) -> Optional[str]:
        """Find NSSM executable, install if needed.

        Returns:
            Path to nssm.exe, or None if can't install
        """
        import shutil

        # Check if NSSM is on PATH
        nssm = shutil.which("nssm")
        if nssm:
            return nssm

        # Check CSC bin directory
        csc_root = os.environ.get("CSC_ROOT", "C:\\csc")
        bin_nssm = Path(csc_root) / "bin" / "nssm.exe"
        if bin_nssm.exists():
            return str(bin_nssm)

        # Try to download and extract NSSM (requires requests)
        try:
            return self._download_nssm(csc_root)
        except Exception as e:
            print(f"[WARN] Could not install NSSM: {e}")
            return None

    def _download_nssm(self, csc_root: str) -> str:
        """Download and extract NSSM to csc/bin/.

        Returns:
            Path to nssm.exe
        """
        import zipfile
        import tempfile
        import urllib.request

        print(f"[INFO] Downloading NSSM {self.NSSM_VERSION}...")

        # Download to temp dir
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "nssm.zip"
            urllib.request.urlretrieve(self.NSSM_URL, str(zip_path))

            # Extract
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(tmpdir)

            # Find nssm.exe (it's nested in a directory)
            nssm_exe = None
            for root, dirs, files in os.walk(tmpdir):
                if "nssm.exe" in files:
                    nssm_exe = Path(root) / "nssm.exe"
                    break

            if not nssm_exe:
                raise FileNotFoundError("nssm.exe not found in archive")

            # Copy to csc/bin
            bin_dir = Path(csc_root) / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            dest = bin_dir / "nssm.exe"
            import shutil
            shutil.copy(str(nssm_exe), str(dest))

            print(f"[OK] NSSM installed to {dest}")
            return str(dest)

    def install(self, service_name: str, config: dict) -> Tuple[bool, str]:
        """Install a service using NSSM.

        Args:
            service_name: "server", "bridge", etc.
            config: Service config dict

        Returns:
            (success, message)
        """
        if not self.nssm_path:
            return (False, "NSSM not available and could not be installed")

        # Uppercase service name for Windows
        win_service_name = f"CSC-{service_name.upper()}"

        # Check if already installed
        if WindowsServiceDetector.service_exists(win_service_name):
            return (False, f"Service {win_service_name} already installed")

        try:
            # Build command for the service
            module = config.get("module", "")
            if not module:
                return (False, f"No module specified in config")

            # Full command to run
            python_exe = sys.executable
            cmd = f'"{python_exe}" -m {module}'

            # Log file
            log_dir = config.get("log_file", "C:\\csc\\logs").rsplit("\\", 1)[0]
            log_file = f"{log_dir}\\{service_name}.log"

            # Install via NSSM
            install_cmd = [
                str(self.nssm_path), "install",
                win_service_name,
                python_exe,
                f"-m {module}"
            ]

            import subprocess
            result = subprocess.run(install_cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return (False, f"NSSM install failed: {result.stderr}")

            # Set output file
            output_cmd = [
                str(self.nssm_path), "set",
                win_service_name,
                "AppStdout", log_file
            ]
            subprocess.run(output_cmd, capture_output=True)

            # Set startup to auto if configured
            if config.get("auto_start"):
                startup_cmd = [
                    str(self.nssm_path), "set",
                    win_service_name,
                    "Start", "SERVICE_AUTO_START"
                ]
                subprocess.run(startup_cmd, capture_output=True)

            return (True, f"Service {win_service_name} installed successfully")

        except Exception as e:
            return (False, f"Error installing service: {str(e)}")

    def uninstall(self, service_name: str) -> Tuple[bool, str]:
        """Uninstall a service."""
        if not self.nssm_path:
            return (False, "NSSM not available")

        win_service_name = f"CSC-{service_name.upper()}"

        if not WindowsServiceDetector.service_exists(win_service_name):
            return (False, f"Service {win_service_name} not installed")

        try:
            import subprocess
            cmd = [str(self.nssm_path), "remove", win_service_name, "confirm"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return (False, f"NSSM remove failed: {result.stderr}")

            return (True, f"Service {win_service_name} uninstalled")

        except Exception as e:
            return (False, f"Error uninstalling: {str(e)}")

    def start(self, service_name: str) -> Tuple[bool, str]:
        """Start a service."""
        if not self.nssm_path:
            return (False, "NSSM not available")

        win_service_name = f"CSC-{service_name.upper()}"

        try:
            import subprocess
            cmd = [str(self.nssm_path), "start", win_service_name]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return (False, f"Failed to start {win_service_name}: {result.stderr}")

            return (True, f"Service {win_service_name} started")

        except Exception as e:
            return (False, f"Error starting service: {str(e)}")

    def stop(self, service_name: str) -> Tuple[bool, str]:
        """Stop a service."""
        if not self.nssm_path:
            return (False, "NSSM not available")

        win_service_name = f"CSC-{service_name.upper()}"

        try:
            import subprocess
            cmd = [str(self.nssm_path), "stop", win_service_name]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return (False, f"Failed to stop {win_service_name}: {result.stderr}")

            return (True, f"Service {win_service_name} stopped")

        except Exception as e:
            return (False, f"Error stopping service: {str(e)}")

    def status(self, service_name: str) -> dict:
        """Get service status."""
        win_service_name = f"CSC-{service_name.upper()}"
        detector_status = WindowsServiceDetector.get_service_status(win_service_name)

        if detector_status:
            return {
                "exists": True,
                "running": detector_status.get("Status") == "Running",
                "name": win_service_name,
                "status": detector_status.get("Status"),
                "startup_type": detector_status.get("StartType")
            }
        else:
            return {
                "exists": False,
                "running": False,
                "name": win_service_name
            }
```

---

## Verification Checklist

- [ ] `WindowsServiceProvider` class created
- [ ] `_find_or_install_nssm()` finds NSSM or downloads it
- [ ] `install()` creates service via NSSM
- [ ] `uninstall()` removes service
- [ ] `start()` and `stop()` work
- [ ] `status()` returns correct info
- [ ] Test on Windows system
- [ ] NSSM downloads and installs if not present (check C:\csc\bin\nssm.exe)

---

## Commit

```
feat: Implement Windows service installation with NSSM

- Auto-detect or download NSSM (Non-Sucking Service Manager)
- Install services via NSSM (CSC-Server, CSC-Bridge, etc.)
- Configure logging and auto-start
- Support service start/stop/uninstall operations
- WindowsServiceProvider implements ServiceProvider interface
```

