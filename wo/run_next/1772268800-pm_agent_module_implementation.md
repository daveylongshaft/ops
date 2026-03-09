# PM Agent Module Implementation

## Objective
Create an automated Project Manager agent that handles workorder prioritization, agent selection, batching, and self-healing with opus backup and haiku debugging.

## Core Behavior (95% scripted)

### Decision Framework
Priority order: Infrastructure → Bug fixes → Test fixes → Docstrings → Docs → Features

### Agent Selection Cascade
1. **gemini-3-pro** - coding, complex reasoning (first choice)
2. **gemini-2.5-pro** - coding, moderate (fallback)
3. **gemini-3-flash-preview** - coding, fast (if others hit limits)
4. **gemini-2.5-flash-lite** - docs, text (non-coding)
5. **haiku** - batch same-kind with caching (reliable fallback)
6. **opus** - PM self-healing (last resort)

### Batching Rules
- Group same-kind workorders (all test fixes, all docs, etc.)
- Anthropic agents use prompt caching (shared system prompt)
- Gemini agents run one at a time (no batch API)

### Key PM Logic
- Infrastructure changes cascade to bug fixes and tests
- After infra changes, regenerate test fixes via test-runner
- Docstring regen after code changes keeps maps accurate
- Hold feature WOs until infra/fixes stabilize
- Track agent performance (completion rate per agent type)

## Self-Healing Capability

### Opus Self-Fix (on process failure)
- Spawn opus agent with FULL codemaps + pm context
- Give opus read+write to PM module source
- Task: Fix the PM module logic that failed
- Opus can modify queue_worker integration, batching logic, selection rules
- After fix, PM resumes normal operation

### Haiku Debug (on persistent workorder failure)
- When a workorder fails 3+ times with different agents
- Spawn haiku to examine why it's failing
- Read: Full workorder, agent logs, error patterns
- Task: Identify root cause (path issue? API limit? code problem?)
- Generate diagnostic report or create resolution workorder
- Resume processing with findings

## API Key Management
- Track exhaustion patterns (which key depletes fastest)
- Auto-rotate when quota hit
- Rate keys in .env based on usage patterns
- Fallback chain: KEY_1 → KEY_2 → haiku batch caching

## Outputs & Monitoring
- PM execution journal (decisions, cascades, agent selections)
- Workorder status tracking (ready/wip/done/hold/retry counts)
- Agent performance metrics (completion rate, time, cost)
- API key depletion tracking
- Self-heal event log (when/why opus was invoked)

## Implementation Notes
- 95% of logic should be deterministic/scripted
- Only spawn agents for: self-fix (opus), debugging (haiku), or normal work
- Use PM journal for audit trail and learning
- Can modify itself (PM module code) via opus but not other code
- All PM decisions logged with rationale for traceability
