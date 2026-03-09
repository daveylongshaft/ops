# platform_00: Extend platform.py with RuntimeStrategy Class

**Objective:** Add `RuntimeStrategy` class to detect and track available runtimes (native, WSL, Docker).

**Time:** ~45 minutes | **Difficulty:** Easy | **Next:** platform_01

---

## Task

Add a new `RuntimeStrategy` class to `packages/csc-shared/csc_shared/platform.py` that:

1. **Detects available runtimes** on the current system
2. **Stores detection results** in platform.json
3. **Provides methods** to query runtime info

---

## File to Edit

**`packages/csc-shared/csc_shared/platform.py`**

Current structure: `Root → Log → Data → Version → Platform → Network → Service`

Add `RuntimeStrategy` class **after the `Network` class, before or alongside `Service`**.

---

## Implementation

### Class Definition

```python
class RuntimeStrategy:
    """Detect and manage available runtime environments."""

    def __init__(self, platform_data: dict):
        """Initialize with platform data."""
        self.platform_data = platform_data
        self.available = []
        self.preferred = None
        self.config = {}
        self._detect()

    def _detect(self):
        """Detect available runtimes on current system."""
        # Check native Python
        self._check_native()

        # Check WSL (Windows only)
        if self.platform_data.get("os") == "windows":
            self._check_wsl()

        # Check Docker
        self._check_docker()

        # Set default preferred if any available
        if self.available:
            self.preferred = self.available[0]

    def _check_native(self):
        """Check if native Python runtime is available."""
        import sys
        import shutil

        python_path = sys.executable
        if python_path and shutil.which("python3"):
            self.available.append("native")
            self.config["native"] = {
                "python_path": python_path,
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
                "type": "native"
            }

    def _check_wsl(self):
        """Check if WSL is available (Windows only)."""
        import subprocess
        import shutil

        if not shutil.which("wsl"):
            return

        try:
            # Try to detect WSL distro
            result = subprocess.run(
                ["wsl", "--list", "--verbose"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.available.append("wsl")

                # Extract first running distro name (if available)
                distro_name = "Ubuntu"  # Default
                for line in result.stdout.split("\n"):
                    if "*" in line or "Running" in line:
                        parts = line.split()
                        if parts:
                            distro_name = parts[0].strip("*")
                            break

                self.config["wsl"] = {
                    "distro": distro_name,
                    "type": "wsl",
                    "python_path": "/usr/bin/python3"  # WSL default
                }
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass

    def _check_docker(self):
        """Check if Docker is available."""
        import shutil

        if shutil.which("docker"):
            self.available.append("docker")
            self.config["docker"] = {
                "type": "docker",
                "runtime": "docker"
            }

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return {
            "available": self.available,
            "preferred": self.preferred,
            "config": self.config
        }

    def get_runtime_config(self, runtime: str) -> dict:
        """Get config for specific runtime."""
        return self.config.get(runtime, {})

    def is_available(self, runtime: str) -> bool:
        """Check if runtime is available."""
        return runtime in self.available
```

---

## Integration with Platform Class

Find the `Platform` class (or wherever platform hierarchy ends). Add this method:

```python
def get_runtime_strategy(self) -> RuntimeStrategy:
    """Get runtime strategy info."""
    if not hasattr(self, '_runtime_strategy'):
        self._runtime_strategy = RuntimeStrategy(self.to_dict())
    return self._runtime_strategy
```

And add to the `to_dict()` method output:

```python
def to_dict(self) -> dict:
    data = {
        # ... existing code ...
        "runtime_strategy": self.get_runtime_strategy().to_dict()
    }
    return data
```

---

## Testing

After implementation, test in Python:

```python
from csc_shared.platform import Platform

p = Platform()
rt = p.get_runtime_strategy()

print(f"Available runtimes: {rt.available}")
print(f"Preferred: {rt.preferred}")
print(f"Config: {rt.config}")

# Check if WSL available (if on Windows)
if rt.is_available("wsl"):
    print(f"WSL distro: {rt.get_runtime_config('wsl')['distro']}")
```

---

## Verification Checklist

- [ ] `RuntimeStrategy` class added to platform.py
- [ ] `_detect()` method detects native, WSL, Docker correctly
- [ ] `to_dict()` returns proper JSON-serializable dict
- [ ] `Platform.get_runtime_strategy()` returns RuntimeStrategy instance
- [ ] `Platform.to_dict()` includes runtime_strategy key
- [ ] Test script runs without errors
- [ ] Detection works on your current system (show output in commit)

---

## Commit

```
feat: Add RuntimeStrategy class to detect available runtimes

- Detects native Python, WSL (Windows), Docker availability
- Stores config in platform data
- Platform.to_dict() includes runtime_strategy section
- Test on [your system type]: [output]
```

