# platform_02: Add CommandBuilder Class to platform.py

**Objective:** Add `CommandBuilder` class to auto-generate platform-specific commands (shell syntax, path translation, wrappers).

**Depends on:** platform_00, platform_01
**Time:** ~50 minutes | **Difficulty:** Medium | **Next:** platform_03

---

## Task

Add `CommandBuilder` class that generates proper shell commands for:
- Python module execution (`python3 -m csc_service.server.main`)
- WSL wrapping (when running on Windows but command targets WSL)
- Docker wrapping (when targeting Docker)
- Path translation in commands

---

## File to Edit

**`packages/csc-shared/csc_shared/platform.py`**

Add `CommandBuilder` class **after `PathTranslator`**.

---

## Implementation

```python
class CommandBuilder:
    """Build platform-specific commands with correct syntax and paths."""

    def __init__(self, platform_data: dict, runtime_strategy: RuntimeStrategy, path_translator: PathTranslator):
        """Initialize with platform info."""
        self.platform_data = platform_data
        self.runtime = runtime_strategy
        self.paths = path_translator
        self.os_type = platform_data.get("os")  # "windows" or "linux"
        self.current_runtime = runtime_strategy.preferred

    def build_python_module_cmd(self, module: str, args: str = "", target_runtime: str = None) -> str:
        """Build command to run Python module.

        Args:
            module: Module path like "csc_service.server.main"
            args: Additional arguments to pass to module
            target_runtime: Target runtime (default: current)

        Returns:
            Full command string ready for shell
        """
        if target_runtime is None:
            target_runtime = self.current_runtime

        # Base command
        python_cmd = "python3" if target_runtime != "native" or self.os_type != "windows" else "python3"
        cmd = f"{python_cmd} -m {module}"

        if args:
            cmd += f" {args}"

        # Wrap for target runtime if needed
        return self._wrap_for_runtime(cmd, target_runtime)

    def build_service_start_cmd(self, service_name: str, target_runtime: str = None) -> str:
        """Build command to start a service.

        Args:
            service_name: "server", "bridge", "queue-worker", etc.
            target_runtime: Target runtime (default: current)

        Returns:
            Full command string
        """
        if target_runtime is None:
            target_runtime = self.current_runtime

        # Map service names to modules
        module_map = {
            "server": "csc_service.server.main",
            "bridge": "csc_service.bridge.main",
            "queue-worker": "csc_service.infra.queue_worker",
            "client": "csc_service.client.main",
            "pm": "csc_service.infra.pm",
        }

        module = module_map.get(service_name)
        if not module:
            raise ValueError(f"Unknown service: {service_name}")

        return self.build_python_module_cmd(module, target_runtime=target_runtime)

    def _wrap_for_runtime(self, cmd: str, target_runtime: str) -> str:
        """Wrap command for target runtime.

        Examples:
            Python on WSL → "wsl -- python3 -m ..."
            Python on Docker → "docker exec csc python3 -m ..."
        """
        if target_runtime == "wsl":
            # If current is Windows native, add "wsl --"
            if self.current_runtime == "native" and self.os_type == "windows":
                return f"wsl -- {cmd}"
            # If already in WSL, no wrapping
            return cmd

        elif target_runtime == "docker":
            # Run in docker container
            return f"docker exec -i csc {cmd}"

        # Native or Linux - no wrapping needed
        return cmd

    def build_cd_cmd(self, path: str, target_runtime: str = None) -> str:
        """Build 'cd' command for target runtime."""
        if target_runtime is None:
            target_runtime = self.current_runtime

        # Translate path
        translated_path = self.paths.translate(path, target_runtime)

        # Escape spaces in path if needed
        if " " in translated_path:
            translated_path = f'"{translated_path}"'

        return f"cd {translated_path}"

    def build_chain_cmd(self, commands: list, target_runtime: str = None) -> str:
        """Build chained command (cd && cmd1 && cmd2).

        Args:
            commands: List of (description, command) tuples
            target_runtime: Target runtime

        Returns:
            Full chained command with && separators
        """
        if target_runtime is None:
            target_runtime = self.current_runtime

        cmd_parts = []
        for cmd in commands:
            if isinstance(cmd, tuple):
                _, cmd_str = cmd
            else:
                cmd_str = cmd
            cmd_parts.append(cmd_str)

        # Join with && for sequential execution
        full_cmd = " && ".join(cmd_parts)

        # Wrap entire chain if needed
        return self._wrap_for_runtime(full_cmd, target_runtime)

    def build_env_cmd(self, env_vars: dict, cmd: str, target_runtime: str = None) -> str:
        """Build command with environment variables.

        Args:
            env_vars: Dict of env var names and values
            cmd: Command to run with these env vars
            target_runtime: Target runtime

        Returns:
            Full command with environment variables
        """
        if target_runtime is None:
            target_runtime = self.current_runtime

        # For Unix-like shells
        env_part = " ".join([f"{k}={v}" for k, v in env_vars.items()])
        full_cmd = f"{env_part} {cmd}"

        return self._wrap_for_runtime(full_cmd, target_runtime)

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return {
            "os_type": self.os_type,
            "current_runtime": self.current_runtime,
            "available_runtimes": self.runtime.available
        }
```

---

## Integration with Platform Class

Add method to `Platform` class:

```python
def get_command_builder(self) -> CommandBuilder:
    """Get command builder for this platform."""
    if not hasattr(self, '_command_builder'):
        rt = self.get_runtime_strategy()
        pt = self.get_path_translator()
        self._command_builder = CommandBuilder(self.to_dict(), rt, pt)
    return self._command_builder
```

---

## Testing

Create test script:

```python
from csc_shared.platform import Platform

p = Platform()
cb = p.get_command_builder()

# Test Python module command
print("Python command:")
print(cb.build_python_module_cmd("csc_service.server.main"))

# Test service start
print("\nServer start command:")
print(cb.build_service_start_cmd("server"))

# Test bridge start
print("\nBridge start command:")
print(cb.build_service_start_cmd("bridge"))

# Test chained command
print("\nChained command:")
cmds = [
    ("change dir", "cd /c/csc"),
    ("start server", "python3 -m csc_service.server.main")
]
print(cb.build_chain_cmd(cmds))

# Test with env vars
print("\nWith env vars:")
print(cb.build_env_cmd(
    {"PYTHONPATH": "/mnt/c/csc/packages/csc-service"},
    "python3 -m csc_service.server.main"
))

# Test WSL wrapping (if on Windows)
if p.get_runtime_strategy().is_available("wsl"):
    print("\nWSL-wrapped command:")
    print(cb.build_python_module_cmd("csc_service.server.main", target_runtime="wsl"))
```

---

## Verification Checklist

- [ ] `CommandBuilder` class added
- [ ] `build_python_module_cmd()` works for all runtimes
- [ ] `build_service_start_cmd()` maps service names correctly
- [ ] `_wrap_for_runtime()` adds "wsl --" when needed
- [ ] `build_chain_cmd()` joins commands with &&
- [ ] `build_env_cmd()` includes environment variables
- [ ] Test script runs without errors
- [ ] Commands are correct for your current platform
- [ ] WSL wrapping works (if available on your system)

---

## Commit

```
feat: Add CommandBuilder to generate platform-specific commands

- Builds Python module commands with correct syntax
- Wraps for WSL/Docker when needed
- Chains commands with && for sequential execution
- Handles environment variables
- Platform.get_command_builder() returns instance
- Test output: [show commands on your system]
```

