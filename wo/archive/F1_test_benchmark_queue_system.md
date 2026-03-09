# Phase F1: Test Complete Benchmark Queue System

## Task

End-to-end test of the benchmark queue system to verify all components work together.

## Prerequisites

Before running this test, ensure:
- ✅ Phase A1: Queue directories created
- ✅ Phase B1: Queue worker script created
- ✅ Phase C1: benchmark_service updated
- ✅ Phase D1: Task Scheduler configured
- ✅ Phase E1: Wrapper COMPLETE tag verified

## Test Procedure

### 1. Run a Simple Benchmark

```bash
benchmark run hello-world ollama-codellama
```

### 2. Verify Queue Flow

Check that prompt appears in queue:
```bash
ls agents/ollama-codellama/queue/in/
# Should show benchmark-hello-world-*.md
```

Wait for queue worker (runs every 2 minutes):
```bash
# Worker should:
# - Move prompt to queue/work/
# - Spawn wrapper
# - Save .pid file
```

Check work directory:
```bash
ls agents/ollama-codellama/queue/work/
# Should show prompt + .pid file
```

### 3. Monitor Progress

Check WIP file:
```bash
cat prompts/wip/benchmark-hello-world-*.md
# Should show agent's work being journaled
```

Check wrapper is running:
```bash
cat agents/ollama-codellama/queue/work/*.pid
ps aux | grep [PID]
```

### 4. Verify Completion

When agent finishes:
- WIP file should have "COMPLETE" at end
- Prompt moved to prompts/done/
- Result archived in tools/benchmarks/results/
- Git commit created

### 5. Check Results

```bash
ls tools/benchmarks/results/
# Should show new .tgz file

catalog update
catalog rank
# Should show ollama-codellama ranking
```

## Expected Timeline

- Prompt creation: instant
- Queue pickup: within 2 minutes
- Agent execution: 5-10 minutes
- Completion detection: within 2 minutes
- Total: ~15 minutes

## Acceptance Criteria

- ✅ Benchmark creates queue prompt
- ✅ Worker picks up and spawns agent
- ✅ Agent completes task
- ✅ COMPLETE tag detected
- ✅ File moved to done/
- ✅ Result archived
- ✅ Git committed
- ✅ No prompts stuck in ready/wip
- ✅ Ranking updated

## Troubleshooting

If test fails, check:
- Queue worker logs: `logs/queue-worker.log`
- Wrapper logs: `logs/agent_*.log`
- Task Scheduler status
- PID files in queue/work/

## Work Log

---

DEAD END
