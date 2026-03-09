---
requires: [python3, pip]
platform: [windows, linux]
---
# Phase 1: Package Renaming & Cleanup

## Goal
Standardize all package names to use the `csc-` prefix (hyphen) and eliminate `csc_` (underscore) prefixed packages. This ensures consistency and prevents duplicate package installations.

## Steps

1.  **Identify Duplicates:**
    *   List all installed packages matching `csc_` or `csc-`.
    *   Identify which local directories in `packages/` use underscores vs hyphens.

2.  **Uninstall Incorrect Packages:**
    *   Uninstall any installed package starting with `csc_` (e.g., `csc_server`, `csc_client`, `csc_shared`).
    *   Command: `pip uninstall -y csc_server csc_client csc_shared` (and any others found).

3.  **Rename/Update Source:**
    *   Rename directories in `packages/` from `csc_name` to `csc-name` if they exist (e.g., `packages/csc_server` -> `packages/csc-server`).
    *   Update `setup.py` or `pyproject.toml` in each package to ensure the `name` field uses hyphens (e.g., `name="csc-server"`).

4.  **Reinstall Correct Packages:**
    *   Install the renamed packages in editable mode.
    *   Command: `pip install -e packages/csc-server`, `pip install -e packages/csc-client`, etc.

5.  **Verify:**
    *   Run `pip list | grep csc` to confirm only `csc-` packages are installed.
    *   Ensure imports still work (Python treats `csc-server` package as `csc_server` module usually, but we must verify `import csc_server` works).

## Journaling
Journal every step to the WIP file as per project standards.

## Execution Log (Recreated for Audit)
- Agent (gemini-2.5-pro) identified duplicates.
- Agent uninstalled csc_server and csc_shared.
- Agent renamed packages/csc_client to packages/csc-client.
- Agent renamed packages/csc_server to packages/csc-server.
- Agent renamed packages/csc_shared to packages/csc-shared.
- Agent verified pyproject.toml files.
- Agent reinstalled packages in editable mode.
- Agent verified only csc- packages are installed.
- Agent confirmed project consistency.
- [!] Agent incorrectly deleted this WIP file (Corrected by Supervisor).
