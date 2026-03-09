---
urgency: P2
tags: infrastructure,agent-setup,automation
requires: [git, python3]
---

# Setup: Plan Review Agent (Autonomous Jules Plan Approval)

## Objective

Create a specialized agent that reviews Jules-generated plans and approves/denies them autonomously, similar to how pr-review works for GitHub PRs.

## What to Build

### 1. Plan Review Agent Directory

Create: `agents/plan-review/`

```
agents/plan-review/
├── queue/
│   ├── in/          (incoming plans to review)
│   ├── work/        (processing)
│   └── out/         (approved/denied results)
├── context/
│   ├── system.md    (plan review instructions)
│   └── guidelines.md (approval criteria)
└── state.json       (agent metrics)
```

### 2. System Prompt

File: `agents/plan-review/context/system.md`

```markdown
# Plan Review Agent

You are an expert code reviewer specialized in validating Jules-generated plans for bug fixes, refactoring, and feature implementation.

## Your Task

Review Jules coding plans and determine if they should be APPROVED or DENIED.

## Approval Criteria

APPROVE if the plan:
- Correctly addresses the stated bug/feature
- Maintains code quality and project patterns
- Doesn't introduce security issues
- Has reasonable scope (won't take >2 hours to implement)
- Respects existing architecture

DENY if the plan:
- Misunderstands the requirements
- Introduces technical debt or breaks patterns
- Is incomplete or missing critical steps
- Overscopes the work
- Could introduce bugs or security issues

## Output Format

Respond with exactly:

```json
{
  "decision": "APPROVE" or "DENY",
  "reason": "Brief explanation (1-2 sentences)",
  "confidence": 0.95,
  "notes": "Optional detailed notes for Jules"
}
```

Be decisive. Trust your judgment.
```

### 3. Plan Review Polling Service

File: `csc_service/infra/plan_review.py`

```python
"""Autonomous plan review agent service."""

from csc_service.shared.log import Log
from csc_service.shared.platform import Platform
from pathlib import Path
import json
import subprocess
import time

class PlanReview(Log):
    """Review Jules plans autonomously."""

    def __init__(self):
        super().__init__()
        self.plat = Platform()
        self.agent_dir = self.plat.get_abs_root_path(['agents', 'plan-review'])
        self.queue_in = Path(self.agent_dir) / 'queue' / 'in'
        self.queue_out = Path(self.agent_dir) / 'queue' / 'out'

    def run_cycle(self):
        """Poll for pending plans, review each one."""
        self.queue_in.mkdir(parents=True, exist_ok=True)
        self.queue_out.mkdir(parents=True, exist_ok=True)

        pending_plans = list(self.queue_in.glob('*.json'))

        for plan_file in pending_plans:
            self._review_plan(plan_file)

    def _review_plan(self, plan_file: Path):
        """Review single plan via AI agent."""
        try:
            with open(plan_file) as f:
                plan_data = json.load(f)

            session_id = plan_data.get('session_id')
            plan_content = plan_data.get('content')

            # Prompt agent to review
            review_prompt = f"""
Review this Jules plan:

Session: {session_id}

{plan_content}
"""

            # Spawn review agent (using claude or same as queue-worker)
            result = subprocess.run([
                'python', '-m', 'csc_service.clients.claude.main',
                '--system', 'Plan Reviewer',
                '--prompt', review_prompt,
            ], capture_output=True, text=True, timeout=60)

            # Parse decision from output
            decision = self._parse_decision(result.stdout)

            # Store result
            result_file = self.queue_out / f"{session_id}_decision.json"
            with open(result_file, 'w') as f:
                json.dump(decision, f)

            self.log(f"Plan reviewed: {session_id} → {decision['decision']}", "INFO")

            # Move input to processed
            plan_file.unlink()

        except Exception as e:
            self.log(f"Plan review failed: {e}", "ERROR")

    def _parse_decision(self, ai_output: str) -> dict:
        """Extract approval decision from AI output."""
        # Parse JSON from AI response
        try:
            # Find JSON block in output
            import re
            match = re.search(r'\{.*?"decision".*?\}', ai_output, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass

        # Fallback: return default
        return {
            "decision": "DENY",
            "reason": "Could not parse decision",
            "confidence": 0.5,
        }
```

### 4. Integration with Jules Service

Update: `csc_service/clients/julius/julius.py`

```python
def submit_plan_for_review(self, session_id: str, plan_content: str) -> bool:
    """Queue plan for review by plan-review agent."""
    review_dir = self.plat.get_abs_root_path(['agents', 'plan-review', 'queue', 'in'])

    plan_file = Path(review_dir) / f"{session_id}_plan.json"

    with open(plan_file, 'w') as f:
        json.dump({
            'session_id': session_id,
            'content': plan_content,
            'submitted_at': time.time(),
        }, f)

    self.log(f"Plan queued for review: {session_id}", "INFO")
    return True

def check_plan_approval(self, session_id: str) -> dict:
    """Check if plan was approved."""
    review_dir = self.plat.get_abs_root_path(['agents', 'plan-review', 'queue', 'out'])

    decision_file = Path(review_dir) / f"{session_id}_decision.json"

    if decision_file.exists():
        with open(decision_file) as f:
            return json.load(f)

    return None  # Still pending review
```

### 5. PM Logic for Plan Approval

Update: `csc_service/infra/pm.py`

```python
def monitor_julius_plans(self):
    """Check on pending Jules plans, wait for approval."""
    active_sessions = self.load('julius_sessions', {})

    for session_id, info in active_sessions.items():
        if info.get('state') == 'pending_approval':
            # Check if plan-review agent has decided
            decision = self.julius.check_plan_approval(session_id)

            if decision:
                if decision['decision'] == 'APPROVE':
                    self.log(f"Plan approved: {session_id}", "INFO")
                    # Tell Jules to proceed
                    self.julius.approve_plan_via_api(session_id)
                    info['state'] = 'executing'
                else:
                    self.log(f"Plan denied: {session_id}", "WARN")
                    # Reject and log reason
                    info['state'] = 'denied'
                    info['denial_reason'] = decision['reason']

                self.store('julius_sessions', active_sessions)
```

## Workflow

```
Jules generates plan
  ↓
Submit to plan-review queue (queue/in/)
  ↓
plan-review agent polls & reviews
  ↓
Agent outputs decision (queue/out/)
  ↓
PM checks decision
  ↓
If APPROVE: Tell Jules to proceed
If DENY: Reject session, log reason
```

## Success Criteria

✅ Plan review agent directory created
✅ Context/guidelines set up to make good decisions
✅ Agent runs every 60s via service polling
✅ Plans reviewed autonomously (no human required)
✅ Decisions passed back to Jules service
✅ PM integrates approval workflow
✅ Tests verify decision parsing

## Next Steps (After This WO)

1. Create plan-review agent directory
2. Wire plan-review into pm.run_cycle()
3. Update julius.py to queue/check plans
4. Test end-to-end: workorder → Jules → plan review → approval

COMPLETE
