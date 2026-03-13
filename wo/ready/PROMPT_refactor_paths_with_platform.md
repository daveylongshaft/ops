---
urgency: P2
requires: [python3]
---
# Refactor Hardcoded Paths to use Platform Object

**Objective:** Audit the entire CSC codebase for hardcoded file system paths (e.g., `/opt/csc`, `C:\csc`, `/etc/csc`) and refactor them to use the centralized `Platform` object methods.

## Task Description
The project is moving towards a strict platform-independent architecture. Direct path manipulation or assuming specific root locations breaks cross-platform compatibility between Windows, Linux, and Android.

## Requirements
1.  **Audit**: Search for string literals and `Path` objects that use hardcoded absolute paths or manual `PROJECT_ROOT` relative logic.
2.  **Refactor**: Replace these with calls to the `Platform` object:
    -   `Platform.get_etc_dir()` for configuration.
    -   `Platform.get_logs_dir()` for log files.
    -   `Platform.get_wo_dir()` for workorders.
    -   `Platform.get_agents_dir()` for agent directories.
    -   `Platform.get_tools_dir()` for code maps.
    -   `Platform.get_docs_dir()` for documentation.
    -   `Platform.get_backup_dir()` for backups.
    -   `Platform().run_dir` for PID files and sockets.
3.  **Shell Scripts**: Ensure `.sh` and `.bat` scripts use `eval $(csc-platform env)` or `call csc-platform.bat env` to load `CSC_*` environment variables instead of hardcoding paths.
4.  **Consistency**: Use `Platform.PROJECT_ROOT` as the sole source of truth for the root directory.

## Success Criteria
-   No hardcoded absolute paths remain in the core service modules or CLI tools.
-   The system remains fully functional on both Windows and Linux without manual path configuration.
-   `csc-ctl status` correctly reports state by resolving PID files via `Platform`.
