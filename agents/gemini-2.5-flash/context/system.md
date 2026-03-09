# System Context: Qwen Integration Fix

## Your Role
You are debugging and fixing the qwen/ollama integration in the CSC system. The goal is to make ollama-qwen work with `agent assign` using the agent-wrapper.

## Current Problem
- ollama-agent is exiting with code 1
- Benchmarks fail when assigned to ollama-qwen
- The agent-wrapper is calling ollama-agent but something is failing

## What Has Already Been Fixed
1. agent-wrapper now passes `-p -` flag to ollama-agent for stdin input
2. Template copying is in place for queue-based task files
3. agent_service.py updated to use new wrapper path

## What You Need to Do
1. Diagnose why ollama-agent is still failing (likely ollama service issue)
2. Fix the root cause based on your diagnostics
3. Verify the full pipeline works: agent assign → wrapper → ollama-agent → completion
4. Validate with 3 successful benchmark runs

## Key Files
- `/c/csc/bin/ollama-agent.BAT` - The ollama agent binary
- `/c/csc/bin/agent-wrapper` - The universal wrapper
- `/c/csc/agents/templates/default.md` - Queue task template
- `/c/csc/logs/agent_*.log` - Recent agent logs with failure details

## Success Criteria
- ollama-agent responds to stdin input with `-p -` flag
- Prompts move: ready → wip → done (not back to ready)
- benchmark hello-world runs successfully 3 times with qwen
