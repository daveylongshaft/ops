---
requires: [python3, git, npx]
platform: [windows, linux, macos]
agent: gemini-2.5-pro
---
# Workorder: Refactor Agent Service for orders.md Workflow

**Goal:** Correctly implement the workorder processing workflow where the `assign` method of `agent_service.py` uses a helper script to generate an `orders.md` file in the agent's queue, and the `run_agent` scripts consume this `orders.md` file.

**Context:**
The previous attempts to assign and run workorders failed due to `agent_service.py` incorrectly handling the `orders.md` generation and `run_agent` scripts not correctly consuming the prompt. The user has clarified the precise workflow:
-   `agent_service.py::assign` should call a helper script (`generate_orders_md.sh/.bat`).
-   This helper script creates `agents/<agent_name>/queue/in/orders.md`.
-   The content of `orders.md` is the template with `<wip_file_relative_pathspec>` replaced by the actual WIP file's relative path.
-   The `run_agent` script then reads `orders.md` and uses the path within it to find the actual WIP file.

**Current Progress:**
-   Created `agents/templates/generate_orders_md.sh` and `generate_orders_md.bat`. These scripts take `AGENT_DIR`, `WIP_RELATIVE_PATH`, and `TEMPLATE_PATH`, and correctly perform the replacement, outputting to `agents/<AGENT_NAME>/queue/in/orders.md`.
-   Attempted to modify `agent_service.py` to call these scripts, but the `replace` tool failed due to `old_string` mismatch.

**Tasks:**

1.  **Modify `agent_service.py` (`assign` method):**
    *   Remove the existing template reading, workorder content reading, content combination, and `orders.md` writing logic.
    *   Replace it with a call to the new `generate_orders_md.sh` (or `.bat`) script, passing `agent_dir`, `wip_relative_path`, and the resolved `template_to_use`.
    *   Ensure error handling is in place for the `subprocess.run` call.

2.  **Update `run_agent.sh` and `run_agent.bat` (specific and template versions):**
    *   Modify these scripts to expect the primary prompt content (containing the WIP relative path) to be read from `orders.md` in their working directory (which will be `agents/<agent_name>/queue/work/`).
    *   Ensure they correctly parse `orders.md` to extract the `wip_relative_path`.
    *   Use this `wip_relative_path` to read the actual WIP file.
    *   Adjust how `npx @google/gemini-cli` is called to incorporate this new workflow (e.g., passing the WIP file path directly or letting `npx` read it).

**Validation:**
-   Assign a workorder and verify `orders.md` is correctly generated in `queue/in/`.
-   Verify `run_agent` script successfully processes `orders.md`, reads the WIP file, and executes the agent.
-   Ensure the agent marks the workorder as COMPLETE upon success.

**Journaling Protocol:**
-   Journal EVERY step before executing it to this WIP file.
