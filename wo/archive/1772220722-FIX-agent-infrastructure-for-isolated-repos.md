---
requires: [python3, bash]
platform: [windows, linux]
---

# FIX: Agent Infrastructure - Isolated Repos per Agent

## Problem

Current agent setup is broken:
1. **Claude nesting**: Can't invoke Claude CLI from within Claude Code session
2. **Agent isolation**: All agents run in main /csc directory, causing conflicts
3. **No separate repos**: Agents need isolated git repos to work independently
4. **run_agent scripts**: Won't work without proper isolated environment

## Solution

Each agent gets:
- Isolated git clone in `/csc/agents/<agent-name>/repo/` 
- Working directory at `/csc/agents/<agent-name>/work/`
- Agent-specific run script that cd's to isolated repo before invoking

### Implementation

1. **Update agent_service.py**
   - Replace cagent references with direct agent invocation
   - For Claude/Haiku/Opus: Use subprocess with proper PYTHONPATH
   - For Gemini: Route through IRC server (already built-in)
   - For others: Use existing binary

2. **Create isolated repo structure**
   - `agents/<name>/repo/` → git clone
   - `agents/<name>/work/` → temp work directory
   - `agents/<name>/bin/run_agent_isolated.sh` → runs in isolated context

3. **Fix nested session issue**
   - Run agent as subprocess with separate Python interpreter
   - Do NOT invoke Claude Code CLI directly
   - Use agent module imports directly: `from csc_service.clients.claude.main import main`

4. **Test with isolated agent**
   - Create test workorder
   - Assign to haiku with isolated repo
   - Verify WIP grows, agent completes successfully

## Critical Files to Modify

- `packages/csc-service/csc_service/shared/services/agent_service.py`
- `agents/*/bin/run_agent_isolated.sh` (create new)
- `agents/haiku/orders.md-template` (update to work in isolated context)

## Acceptance Criteria

- ✓ Agent assign works without segfault
- ✓ Agent runs in isolated repo clone
- ✓ WIP file grows with agent progress  
- ✓ Agent completes successfully
- ✓ Works for Claude (haiku), Gemini, and other agents
- ✓ No nested Claude Code sessions

## Status

Ready for assignment to sonnet (needs deep infrastructure work)


--- AUDIT [2026-02-27 13:22] ---
INCOMPLETE
Pending:
  - No Work Log section present - file lacks agent activity documentation
  - No COMPLETE marker - work log should end with 'COMPLETE'
  - No evidence of actual implementation - critical files listed but no indication they were modified
  - No test results - acceptance criteria listed but no verification that tests passed
  - No subprocess/PYTHONPATH modifications documented - key solution (step 3) not verified
  - No isolated repo structure creation evidence - agents/<name>/repo/, work/, bin/ not confirmed created
  - No agent_service.py changes logged - primary file needing modification has no documented changes
This is a design/planning document with no work log showing implementation was completed - it describes what needs to be done but has no evidence that it was actually done.


DEAD END - Fix already applied in current codebase
