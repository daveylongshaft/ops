# platform_01: Add PathTranslator Class to platform.py

**Objective:** Add `PathTranslator` class to auto-convert paths between Windows, WSL, and Docker formats.

**Depends on:** platform_00 (RuntimeStrategy)
**Time:** ~50 minutes | **Difficulty:** Medium | **Next:** platform_02

---

## Task

Add `PathTranslator` class that translates file paths between formats:
- Windows: `C:\csc\data\file.json`
- WSL: `/mnt/c/csc/data/file.json`
- Docker: `/app/csc/data/file.json`
- Linux/Debian: `/opt/csc/data/file.json`

---

## File to Edit

**`packages/csc-shared/csc_shared/platform.py`**

Add `PathTranslator` class **after `RuntimeStrategy`**.

---

## Implementation

```python
class PathTranslator:
    """Translate file paths between runtime formats."""

    def __init__(self, platform_data: dict, runtime_strategy: RuntimeStrategy):
        """Initialize with platform and runtime info."""
        self.platform_data = platform_data
        self.runtime = runtime_strategy
        self.runtime_type = runtime_strategy.preferred

        # Base paths for each runtime type
        self.base_paths = {
            "native": self._get_native_base(),
            "wsl": "/mnt/c/csc",
            "docker": "/app/csc",
            "linux": "/opt/csc",
            "macos": "/opt/csc"
        }

    def _get_native_base(self) -> str:
        """Get native base path (Windows or Linux)."""
        import os
        if self.platform_data.get("os") == "windows":
            return "C:\\csc"  # Windows native
        else:
            return "/opt/csc"  # Linux/macOS

    def translate(self, path: str, target_runtime: str = None) -> str:
        """Translate path to target runtime format.

        Args:
            path: Path in any format (auto-detected)
            target_runtime: Target format (default: self.runtime_type)

        Returns:
            Translated path
        """
        if target_runtime is None:
            target_runtime = self.runtime_type

        # Normalize the input path
        normalized = self._normalize_path(path)

        # Convert to target runtime
        return self._convert_to_runtime(normalized, target_runtime)

    def _normalize_path(self, path: str) -> str:
        """Normalize path to internal format (always forward slashes, relative to csc root)."""
        import os

        # Convert backslashes to forward slashes
        path = path.replace("\\", "/")

        # Remove 'C:' or '/mnt/c' prefixes (make relative to csc root)
        path = path.replace("C:/", "")
        path = path.replace("/mnt/c/", "")
        path = path.replace("/opt/", "")
        path = path.replace("/app/", "")

        # Remove 'csc/' prefix if present
        if path.startswith("csc/"):
            path = path[4:]

        return path

    def _convert_to_runtime(self, rel_path: str, target_runtime: str) -> str:
        """Convert normalized relative path to target runtime format."""
        base = self.base_paths.get(target_runtime)
        if not base:
            raise ValueError(f"Unknown runtime: {target_runtime}")

        # For Windows native, use backslashes
        if target_runtime == "native" and self.platform_data.get("os") == "windows":
            rel_path = rel_path.replace("/", "\\")
            return f"{base}\\{rel_path}" if rel_path else base

        # For all others, use forward slashes
        return f"{base}/{rel_path}" if rel_path else base

    def auto_translate(self, path: str) -> str:
        """Auto-detect source format and translate to current runtime."""
        # If path contains backslashes, likely Windows
        # If path contains /mnt/c, likely WSL
        # If path contains /opt/, likely Linux
        # If path contains /app/, likely Docker

        # Just normalize and convert - detection happens naturally
        return self.translate(path, self.runtime_type)

    def to_native(self, path: str) -> str:
        """Convert to native Windows/Linux path."""
        native_type = "native" if self.platform_data.get("os") == "windows" else "linux"
        return self.translate(path, native_type)

    def to_wsl(self, path: str) -> str:
        """Convert to WSL path format."""
        return self.translate(path, "wsl")

    def to_docker(self, path: str) -> str:
        """Convert to Docker path format."""
        return self.translate(path, "docker")

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return {
            "runtime_type": self.runtime_type,
            "base_paths": self.base_paths
        }
```

---

## Integration with Platform Class

Add method to `Platform` class:

```python
def get_path_translator(self) -> PathTranslator:
    """Get path translator for this platform."""
    if not hasattr(self, '_path_translator'):
        rt = self.get_runtime_strategy()
        self._path_translator = PathTranslator(self.to_dict(), rt)
    return self._path_translator
```

---

## Testing

Create test script to verify path translations:

```python
from csc_shared.platform import Platform

p = Platform()
pt = p.get_path_translator()

# Test Windows path
print(f"Windows path: {pt.to_native('C:\\csc\\data\\file.json')}")

# Test WSL path
print(f"WSL path: {pt.to_wsl('C:\\csc\\data\\file.json')}")

# Test Docker path
print(f"Docker path: {pt.to_docker('C:\\csc\\packages\\csc-service')}")

# Test auto-translate (to current runtime)
print(f"Current runtime: {pt.auto_translate('C:\\csc\\data\\channels.json')}")
```

---

## Verification Checklist

- [ ] `PathTranslator` class added to platform.py
- [ ] `_normalize_path()` correctly removes prefixes
- [ ] `_convert_to_runtime()` produces correct formats for each runtime
- [ ] `translate()` and shortcut methods (`to_native()`, `to_wsl()`, etc.) work
- [ ] Auto-translate correctly detects source and converts
- [ ] Test script runs and shows correct translations for your system
- [ ] Windows backslash handling works (if on Windows)
- [ ] WSL `/mnt/c/` paths work correctly

---

## Commit

```
feat: Add PathTranslator to auto-convert paths between runtimes

- Converts between Windows, WSL, Docker, Linux path formats
- Normalizes to internal format, converts to target runtime
- Platform.get_path_translator() returns instance
- Test output: [show translations on your system]
```

