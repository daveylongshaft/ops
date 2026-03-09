# Phase A1: Create Queue Directory Structure

## Task

Create the agents queue directory structure for the benchmark queue system.

## Requirements

Create the following directory structure:
```
agents/
  ollama-codellama/
    queue/
      in/
      work/
  ollama-deepseek/
    queue/
      in/
      work/
  ollama-qwen/
    queue/
      in/
      work/
  haiku/
    queue/
      in/
      work/
  sonnet/
    queue/
      in/
      work/
  opus/
    queue/
      in/
      work/
  gemini-2.5-flash/
    queue/
      in/
      work/
  gemini-3-flash/
    queue/
      in/
      work/
  gemini-3-pro/
    queue/
      in/
      work/
  gemini-2.5-pro/
    queue/
      in/
      work/
```

## Implementation

Use Python pathlib to create all directories:
```python
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = PROJECT_ROOT / "agents"

agents = [
    "ollama-codellama", "ollama-deepseek", "ollama-qwen",
    "haiku", "sonnet", "opus",
    "gemini-2.5-flash", "gemini-3-flash", "gemini-3-pro", "gemini-2.5-pro"
]

for agent in agents:
    (AGENTS_DIR / agent / "queue" / "in").mkdir(parents=True, exist_ok=True)
    (AGENTS_DIR / agent / "queue" / "work").mkdir(parents=True, exist_ok=True)
```

## Verification

After creation, verify all directories exist:
```bash
ls -R agents/
```

## Acceptance

- All agent directories created
- Each has queue/in/ and queue/work/ subdirectories
- No errors during creation

## Work Log
1. Create queue directories for all agents
2. Verify structure
3. Check in/ and work/ subdirs
