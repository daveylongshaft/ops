---
requires: [python3, git]
platform: [windows, linux, macos]
---
# Project Manager Agent

## Goal
Create an autonomous project manager agent that runs as a CSC IRC client (like csc-claude, csc-gemini) but instead of answering questions, it manages the workorder queue and agent assignments.

## What It Does
1. **Monitors `workorders/ready/`** - watches for new workorders arriving
2. **Decides which agent gets which workorder** based on:
   - Prompt filename prefix (haiku-, sonnet-, opus-, gemini-*) as a hint
   - Task complexity analysis (file count, description keywords, estimated scope)
   - Agent benchmark scores from `benchmarks/catalog.json`
   - Agent availability and current workload
   - Cost optimization (use cheapest agent that can handle the task)
3. **Assigns workorders** via the existing `agent assign` / queue-worker pipeline
4. **Tracks outcomes** - when workorders complete or fail, updates benchmark scores:
   - Duration, pass/fail, cost estimate
   - How many attempts the agent needed (incomplete retries)
   - Feeds results back into `benchmarks/catalog.json`
5. **Runs benchmark prompts** periodically against new or untested agents to build baseline data
6. **Reports status** on request via IRC (PM or channel)

## Architecture
- New package: `packages/csc-pm/` (project manager)
- IRC client that connects like any other bot
- Nick: `PM` or `ProjectMgr`
- Joins `#general` and listens
- Has its own decision loop separate from queue-worker
- Reads `benchmarks/catalog.json` for agent capabilities and scores
- Reads `platform.json` for platform-gated routing
- Uses the existing `agent_service.py` and `workorders_service.py` APIs

## Decision Logic (Pseudocode)
```
for each workorder in ready/:
    complexity = analyze(workorder)  # simple/moderate/complex
    requirements = parse_frontmatter(workorder)  # platform, requires
    candidates = filter_agents(requirements)
    best = rank_by(candidates, complexity, cost, benchmark_scores)
    assign(workorder, best)
```

## Benchmark Integration
- Reads `benchmarks/catalog.json` (already exists with agent specs, scores, costs)
- Updates scores after each workorder completion
- Runs periodic benchmark prompts from `benchmarks/prompts/` to calibrate new agents
- Tracks: avg_duration, success_rate, cost_per_task, tasks_completed

## Key Constraints
- Does NOT replace queue-worker - it feeds INTO queue-worker by moving workorders and setting assignments
- Should be lightweight - no AI API calls for its own decisions, pure logic
- Must handle the prompts/workorders directory duality (check both)
- Cross-platform (Windows, Linux, macOS)

## Verification
- PM connects to CSC server, joins #general
- Place a workorder in ready/ with a haiku- prefix
- PM should pick it up and assign it to haiku within one poll cycle
- PM should report the assignment in channel
