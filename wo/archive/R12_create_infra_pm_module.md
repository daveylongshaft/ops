> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# R12: Create PM (Project Manager) Module

## Depends: R01

## Task
Create the project manager module at `packages/csc-service/csc_service/infra/pm.py`.

This is NEW code (not a copy). The PM auto-assigns workorders to agents.

## Steps
Create `packages/csc-service/csc_service/infra/pm.py` with this content:

```python
"""Project Manager: auto-assigns workorders to agents.

Reads workorders/ready/, classifies by filename pattern,
picks the cheapest capable agent, and assigns via queue-worker.
"""
import json
import subprocess
from pathlib import Path

WORK_DIR = None
STATE_FILE = None

# Agent cost tiers (cheapest first)
AGENTS = [
    {"name": "gemini-2.5-flash-light", "tier": "free", "good_for": ["docs", "validation"]},
    {"name": "gemini-2.5-flash", "tier": "cheap", "good_for": ["docs", "simple-fix", "test-fix"]},
    {"name": "haiku", "tier": "cheap", "good_for": ["test-fix", "simple-fix", "docs"]},
    {"name": "gemini-2.5-pro", "tier": "balanced", "good_for": ["feature", "refactor", "complex-fix"]},
    {"name": "sonnet", "tier": "balanced", "good_for": ["feature", "refactor", "complex-fix"]},
    {"name": "opus", "tier": "premium", "good_for": ["architecture", "critical"]},
]

def setup(work_dir: Path):
    global WORK_DIR, STATE_FILE
    WORK_DIR = work_dir
    STATE_FILE = work_dir / "pm_state.json"

def _load_state():
    if STATE_FILE and STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"assignments": {}, "failures": {}}

def _save_state(state):
    if STATE_FILE:
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")

def classify(filename: str) -> str:
    """Classify workorder by filename pattern."""
    fn = filename.lower()
    if "fix_test_" in fn:
        return "test-fix"
    if "fix_" in fn:
        return "simple-fix"
    if "docs_" in fn or "docstring" in fn or "document_" in fn:
        return "docs"
    if fn.startswith("r") and fn[1:3].isdigit():
        return "refactor"
    return "feature"

def pick_agent(category: str) -> str:
    """Pick cheapest agent capable of this category."""
    for agent in AGENTS:
        if category in agent["good_for"]:
            return agent["name"]
    return "sonnet"  # safe default

def run_cycle() -> list:
    """One PM cycle: scan ready/, assign unassigned workorders.

    Returns list of (filename, agent_name) tuples for new assignments.
    """
    if not WORK_DIR:
        return []

    ready_dir = WORK_DIR / "workorders" / "ready"
    if not ready_dir.exists():
        return []

    state = _load_state()
    assigned = []

    for wo_file in sorted(ready_dir.glob("*.md")):
        fname = wo_file.name
        if fname in state["assignments"]:
            continue  # already assigned or attempted

        category = classify(fname)
        agent = pick_agent(category)

        state["assignments"][fname] = {
            "agent": agent,
            "category": category,
            "status": "assigned",
        }
        assigned.append((fname, agent))

    _save_state(state)
    return assigned
```

## Verification
- `python -c "from pathlib import Path; exec(open('packages/csc-service/csc_service/infra/pm.py').read())"` runs without syntax errors
