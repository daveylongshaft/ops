# Phase C3: Update Benchmark Documentation

## Task

Update benchmark system documentation to reflect the queue-based architecture.

## Requirements

Update the following files:

### 1. BENCHMARKING_COMPLETE.md

Update architecture section to show queue flow:
```
benchmark.run()
  → Creates WIP file in prompts/wip/
  → Creates queue prompt in agents/{agent}/queue/in/
  → Queue worker picks up (periodic)
    → Moves to queue/work/
    → Spawns dc-agent-wrapper
    → Tracks PID
  → Wrapper executes agent
  → Agent works, updates WIP
  → Wrapper detects COMPLETE tag
  → Moves to prompts/done/
  → Archives result .tgz
```

### 2. CATALOG_AND_RANKING.md

Add section on queue system integration:
- How benchmarks use queues
- Queue directory structure
- Worker scheduling

### 3. Create tools/benchmarks/README.md

New file explaining:
- Benchmark creation
- Queue workflow
- Result archival format
- Catalog integration

## Acceptance

- All documentation updated
- Queue workflow clearly explained
- Diagrams/examples provided
- No outdated information

## Work Log
