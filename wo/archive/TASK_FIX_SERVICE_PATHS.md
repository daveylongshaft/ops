task: Fix hardcoded /opt/csc paths in services and unify data files
status: wip
date: 2026-02-19

## Issue
agent_service.py and prompts_service.py use hardcoded /opt/csc paths.
Multiple agent_data.json files exist due to inconsistent project root detection.

## Plan
1. Update agent_service.py to detect project root from Path(__file__).
2. Update prompts_service.py to detect project root from Path(__file__).
3. Ensure both services use the same project root for data files (C:\csc).
4. Remove redundant agent_data.json files.
5. Verify with agents list and prompts list.

## Manual Fixes Applied by Gemini
- Updated agent_service.py PROJECT_ROOT and PROMPTS_BASE.
- Updated prompts_service.py PROMPTS_BASE.
- Updated WIP_SYSTEM_PROMPT and _build_prompt templates in agent_service.py.
- Unified agent_data.json to project root.
- Fixed sys.path in bin/prompts and bin/agents.
- Fixed Service imports in agent_service.py and prompts_service.py.

## Pending Verification
- Run dc-run to ensure agents can now be assigned without path errors.
