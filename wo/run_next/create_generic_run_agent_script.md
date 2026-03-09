---
requires: [python3, git, npx]
platform: [windows, linux, macos]
agent: gemini-2.5-pro
---
# Workorder: Implement Generic run_agent Scripts and Update Agent Service

**Goal:** Standardize agent execution by creating generic `run_agent.sh` and `run_agent.bat` templates in `agents/templates/`. Refactor `agent_service.py` to use these templates as a fallback for remote agents when specific scripts are missing, while preserving `cagent` logic for local agents.

**Context:**
-   Remote agents will use `run_agent` scripts (specific or template).
-   Local agents (`qwen`, `deepseek`, `codellama`) will continue to use `cagent.yaml`.

**Tasks:**

1.  **Create Generic `run_agent` Templates:**
    *   Ensure `agents/templates/run_agent.sh` exists.
    *   Ensure `agents/templates/run_agent.bat` exists.
    *   These templates should:
        *   Accept agent name, prompt content, and WIP file path as arguments.
        *   Detect the agent type to construct the correct command (e.g., `npx @google/gemini-cli` for Gemini, placeholders for others like Anthropic/OpenAI).
        *   Handle logging and mark workorder as COMPLETE on success.

2.  **Update `agent_service.py`:**
    *   Modify the `_build_cmd` method:
        *   Check for agent-specific `run_agent.sh`/`.bat` in `agents/<agent_name>/bin/`.
        *   If not found, use the generic template scripts from `agents/templates/`.
        *   Preserve existing logic for local agents using `cagent.yaml`.
    *   Update the `_detect_agents` method to check for `run_agent.sh`/`.bat` for remote agents.

**Validation:**
-   Verify that agents like `gemini`, `claude`, `chatgpt` can be assigned and run using the generic template or specific scripts.
-   Ensure local agents (`qwen`, `deepseek`, `codellama`) continue to function correctly.

**Journaling Protocol:**
-   Journal EVERY step before executing it.
-   Use the WIP file for step-by-step logging.
