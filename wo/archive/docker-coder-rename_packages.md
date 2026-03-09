---
requires: [docker, git, python3]
platform: [linux, windows]
agent: docker-coder
---

# Rename CSC Packages to csc- Convention (Multi-Host)

## Step 1: Self-Replication & Multi-Host Check
1. Get current hostname: Run `hostname` (Linux) or `$env:COMPUTERNAME` (Windows).
2. Let the hostname be `$HOST`.
3. Check if `prompts/wip/$HOST-docker-coder-rename_packages.md` or `prompts/done/$HOST-docker-coder-rename_packages.md` already exists.
4. If it EXISTS:
   - This machine has already processed or is processing this fix.
   - EXIT IMMEDIATELY to avoid duplicate work.
5. If it DOES NOT exist:
   - Copy this prompt file to `prompts/wip/$HOST-docker-coder-rename_packages.md`.
   - Add your `AGENT_PID` and start time to the NEW file.
   - CONTINUE the process using the NEW file for all journaling.

## Step 2: Uninstall Underscore Packages
Run pip uninstall for all potential csc_ packages to clear the environment:
`pip uninstall -y csc_shared csc_server csc_client csc_gemini csc_claude csc_chatgpt csc_bridge csc_docker`

## Step 3: Rename Package Directories
Check the `packages/` directory. Rename any directory starting with `csc_` to use a hyphen instead.
- `packages/csc_shared` -> `packages/csc-shared`
- `packages/csc_server` -> `packages/csc-server`
- `packages/csc_client` -> `packages/csc-client`
- ... etc.

## Step 4: Update pyproject.toml / setup.py
In each package directory (`packages/csc-*/`):
1. Open `pyproject.toml` (or `setup.py`).
2. Ensure the package `name` uses a hyphen (e.g., `name = "csc-shared"`).
3. Do NOT change internal module imports or names (e.g., the folder `csc_shared` INSIDE `packages/csc-shared/` should remain `csc_shared`).

## Step 5: Reinstall Hyphen Packages
Install all packages in editable mode:
- `pip install -e packages/csc-shared`
- `pip install -e packages/csc-server`
- `pip install -e packages/csc-client`
- ... etc.

## Step 6: Global Path/Reference Verify
Search for all occurrences of `csc_` in the project directory (excluding `.git`, `__pycache__`, and internal module source folders).
- Replace any references to package names or paths that use underscores with hyphens.
- **IMPORTANT**: Do NOT change Python `import` statements or module-level `csc_shared` folder names. We only want to fix path references and package distribution names.

## Step 7: Final Verification
1. Run `csc-server --help` to verify the server entry point works.
2. Run `csc-client --help` to verify the client entry point works.
3. Verify that `AI` commands work on the server.

## Step 8: Complete
Move the host-prefixed WIP file to `prompts/done/`.

--- SESSION 2026-02-19 (haiku) ---
Verified: All packages already use hyphen convention (csc-shared, csc-server, etc.)
No csc_ directories found in packages/. Rename was completed previously.
STATUS: COMPLETE
