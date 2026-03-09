# Phase C1: Fix benchmark_service to Use Queue System

## Task

Update `packages/csc-shared/services/benchmark_service.py` to use the queue system instead of directly calling agent_service.assign().

## Current Problem

The `run()` method directly calls `agent_service.assign()` which spawns wrappers and polls for completion. This causes prompts to get stuck when agents fail.

## Required Changes

**File:** `packages/csc-shared/services/benchmark_service.py`

### Change 1: Update run() method

Instead of:
```python
# Step 2: Assign to agent via agent_service (uses wrapper)
agent_svc = agent_service(dummy_server)
agent_svc.select(agent_name)
assign_result = agent_svc.assign(prompt_filename)
```

Do:
```python
# Step 2: Create WIP file and queue prompt for agent
wip_file = self.PROJECT_ROOT / "prompts" / "wip" / f"{prompt_filename}.md"
wip_file.write_text(prompt_content, encoding='utf-8')

# Create queue prompt that references WIP
queue_prompt = self._build_queue_prompt(agent_name, wip_file, name)
queue_file = self.PROJECT_ROOT / "agents" / agent_name / "queue" / "in" / f"{prompt_filename}.md"
queue_file.write_text(queue_prompt, encoding='utf-8')
```

### Change 2: Add _build_queue_prompt() method

```python
def _build_queue_prompt(self, agent_name, wip_file, benchmark_name):
    """Build prompt for queue system."""
    template = f"""
You are running a benchmark: {benchmark_name}

Your WIP file is located at: {wip_file}

RULES (from README.1shot):
- Do NOT move prompts between directories
- Do NOT run git commands
- Journal all work to the WIP file at {wip_file}
- When complete, add "COMPLETE" tag at end of WIP file

Task details are in the WIP file. Read it and complete the benchmark.
"""
    return template
```

### Change 3: Update polling logic

Poll the WIP file for COMPLETE tag instead of checking done/ directory.

## Acceptance

- benchmark.run() no longer calls agent_service.assign()
- Creates WIP file in prompts/wip/
- Creates queue prompt in agents/{agent}/queue/in/
- Polls WIP file for COMPLETE tag
- Archives results when complete

## Work Log

---

DEAD END - Benchmarks put on back-burner
