---
requires: [python3, docker, git]
platform: [docker]
---
# Fix CSC Naming Convention: csc_ vs csc-

## Recommended Agent: docker-coder

## Goal
Identify and fix all instances where 'csc_' is used incorrectly instead of 'csc-' for package/directory names and ensure consistency with project conventions.
The project's established conventions (from GEMINI.md and README.1st) state:
"All package directories use hyphenated names (csc-server). Python modules inside them use underscores (csc_server)."

This implies that:
- Filesystem directories/paths and `name` in `setup.py` should use `csc-`.
- Python import statements (e.g., `from csc_shared.irc import ...`) should use `csc_`.

The previous task encountered 'No module named 'csc_shared'' which suggests a mismatch where 'csc-shared' directory exists but is not properly mapped to 'csc_shared' for imports, or 'csc_shared' is being sought as a directory name.

## Work Log
AGENT_PID: [AGENT_PID_HERE] starting at [TIMESTAMP_HERE]

## Steps for the Docker Agent:

1.  **Understand Project Convention**: Reconfirm the naming convention as stated in `GEMINI.md` and `README.1st`. (Already done: "All package directories use hyphenated names (csc-server). Python modules inside them use underscores (csc_server).")

2.  **Initial Search for 'csc_'**:
    Use `grep -r "csc_" .` across the entire project to find all occurrences of `csc_`. Store the output for analysis.

3.  **Analyze Each Occurrence**: For each `csc_` instance identified:
    *   **Context**: Determine if it's within a Python import statement, a file path, a directory name, a variable name, a configuration file, documentation, etc.
    *   **Convention Check**:
        *   If it's an **import name** (e.g., `from csc_shared.platform import ...`), it *should* use `csc_`. These instances are likely correct and should be left alone.
        *   If it's a **directory name** or a **package name in `setup.py`** (e.g., `packages/csc_server/` or `name="csc_server"`), it *should* use `csc-`. These instances need to be renamed/fixed.
        *   If it's in documentation or comments, adjust based on the context to reflect the correct convention.

4.  **Identify Inconsistencies**: Create a clear list of identified inconsistencies where `csc_` is used but `csc-` should be, or vice-versa, based on the established convention. For example:
    *   `packages/csc_shared` should be `packages/csc-shared`
    *   `name="csc_shared"` in `setup.py` should be `name="csc-shared"`
    *   `import csc_some_module` should remain `csc_some_module`

5.  **Propose and Apply Fixes**:
    *   For each inconsistency, formulate a precise `replace` tool call.
    *   Prioritize renaming directories first, then updating references.
    *   **CRITICAL**: Ensure renaming directories happens in a way that Python can still find the modules (e.g., update `setup.py` and reinstall in development mode if necessary, or ensure `sys.path` is adjusted for local scripts).
    *   The primary goal is to ensure Python packages (like `csc-shared` which is imported as `csc_shared`) are correctly discovered. This might involve renaming the directory `csc_shared` to `csc-shared` and ensuring `sys.path` or package installation correctly maps `csc_shared` to `csc-shared`.

6.  **Verify Imports (Python scripts)**: After making changes, run a simple Python script to ensure that key imports like `from csc_shared.platform import Platform` are still working. This might involve installing the packages in editable mode within the Docker environment (`pip install -e packages/csc-shared`).

7.  **Commit Changes**: Commit all applied fixes with a clear, descriptive message (e.g., "feat: Standardize CSC naming convention to csc- for directories and csc_ for imports").

8.  **Move to Done**: Move this prompt file to `prompts/done/`.
