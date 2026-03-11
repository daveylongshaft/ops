# platform_13: Create Daily Motive-State Comparison Workorders

**Objective:** Create a system of daily workorders that compare current system state to Central Motive State, identify gaps, and guide action toward alignment.

**Depends on:** platform_12 (EVOLUTION.md complete, Central Motive State defined)
**Time:** ~90 minutes | **Difficulty:** System Design | **Next:** Becomes recurring daily task

---

## Task

Design and create:

1. **Motive State Summary File** — Stores the Central Motive State (reference)
2. **Daily Comparison Script** — Compares current vs ideal state
3. **Template Workorders** — Recurring daily workorders (template)
4. **Metrics Tracking** — Tracks progress toward motive state
5. **Action Guidance** — Suggests next moves based on gaps

---

## Part 1: Store the Central Motive State

Create file: **`docs/MOTIVE_STATE.md`**

```markdown
# Central Motive State

**Last Updated:** [date]
**Defined In:** docs/EVOLUTION.md
**Alignment Tracker:** logs/motive_state_progress.json

---

## The Core Statement

**"Autonomous, Cross-Platform, Self-Orchestrating Multi-AI System"**

### Four Pillars

#### 1. AUTONOMOUS
- **Definition:** Minimal human intervention in day-to-day operations
- **Key Characteristics:**
  - Self-detecting configuration problems
  - Self-healing when possible
  - Self-improving through feedback loops
  - Agents work independently
- **Current Autonomy Score:** [from EVOLUTION.md]
- **Target:** 95%+
- **Key Gap:** [primary thing blocking full autonomy]
- **Next Step:** [what to work on next]

#### 2. CROSS-PLATFORM
- **Definition:** Works identically on any system
- **Key Characteristics:**
  - No manual per-system configuration
  - Automatic adaptation to runtime environment
  - Seamless migration between platforms
  - Universal tooling and scripting
- **Current Cross-Platform Score:** [estimate]
- **Target:** 100%
- **Key Gap:** [primary thing blocking universal portability]
- **Next Step:** [what to work on next]

#### 3. SELF-ORCHESTRATING
- **Definition:** Manages its own queue, priorities, and agent assignment
- **Key Characteristics:**
  - Intelligent workorder routing
  - Priority escalation/demotion
  - Load balancing across models
  - Feedback-driven optimization
- **Current Orchestration Score:** [estimate]
- **Target:** 90%+
- **Key Gap:** [primary thing blocking full orchestration]
- **Next Step:** [what to work on next]

#### 4. MULTI-AI
- **Definition:** Leverages all available models intelligently
- **Key Characteristics:**
  - Model selection by task complexity
  - Cost optimization through batching
  - Prompt caching for efficient reuse
  - Model-specific routing
- **Current Multi-AI Score:** [estimate]
- **Target:** Maximize efficiency (40% of naive cost)
- **Key Gap:** [primary thing blocking full optimization]
- **Next Step:** [what to work on next]

---

## Daily Alignment Questions

These are the questions we ask every day to check alignment:

1. **Autonomy**: Did we reduce manual intervention today? [Y/N]
2. **Cross-Platform**: Did we make something more portable today? [Y/N]
3. **Self-Orchestrating**: Did we improve system decision-making today? [Y/N]
4. **Multi-AI**: Did we improve cost/efficiency today? [Y/N]

---

## Metrics to Track Daily

See: `logs/motive_state_progress.json`

- Autonomy Score (0-100)
- Cross-Platform Score (0-100)
- Orchestration Score (0-100)
- Model Efficiency (% of naive cost)
- Days on aligned development
- Days since misalignment

---

## Decision Rubric

When unsure about a feature/task, use this rubric:

| Question | If YES → Do It | If NO → Deprioritize |
|----------|---|---|
| Does this move us toward autonomy? | ✓ Prioritize | ✗ Reconsider |
| Does this improve cross-platform? | ✓ Prioritize | ✗ Reconsider |
| Does this enable self-orchestration? | ✓ Prioritize | ✗ Reconsider |
| Does this improve multi-AI efficiency? | ✓ Prioritize | ✗ Reconsider |

If any question is "yes", it's aligned. If all "no", it's distraction.

---

## The Next 90 Days

Focal areas to drive toward motive state:

### Week 1-2: Autonomy
- [Specific work toward autonomy]
- [Specific work toward autonomy]

### Week 3-4: Cross-Platform
- [Specific work toward cross-platform]
- [Specific work toward cross-platform]

### Week 5-8: Self-Orchestrating
- [Specific work toward orchestration]
- [Specific work toward orchestration]

### Week 9-12: Multi-AI Efficiency
- [Specific work toward efficiency]
- [Specific work toward efficiency]

```

---

## Part 2: Daily Comparison Script

Create file: **`bin/check_motive_alignment.py`**

```python
#!/usr/bin/env python3
"""
Check daily alignment with Central Motive State.

Compares current system state to MOTIVE_STATE.md and generates report.
Run daily as part of CI/CD or manual check.
"""

import json
from pathlib import Path
from datetime import datetime


class MotiveStateChecker:
    """Check alignment with Central Motive State."""

    MOTIVE_STATE_FILE = Path(__file__).parent.parent / "docs" / "MOTIVE_STATE.md"
    PROGRESS_FILE = Path(__file__).parent.parent / "logs" / "motive_state_progress.json"

    def __init__(self):
        self.motive_state = self._load_motive_state()
        self.progress = self._load_progress()

    def _load_motive_state(self) -> dict:
        """Load motive state from MOTIVE_STATE.md"""
        # Parse markdown, extract key metrics
        # Returns dict with current targets
        return {
            "autonomy_target": 95,
            "cross_platform_target": 100,
            "orchestration_target": 90,
            "efficiency_target": 40  # percent of naive cost
        }

    def _load_progress(self) -> dict:
        """Load progress history"""
        if not self.PROGRESS_FILE.exists():
            return {"scores": [], "last_check": None}

        with open(self.PROGRESS_FILE) as f:
            return json.load(f)

    def check_alignment(self) -> dict:
        """Check current state vs motive state"""
        from csc_shared.platform import Platform

        p = Platform()

        # Measure current state
        scores = {
            "autonomy": self._measure_autonomy(p),
            "cross_platform": self._measure_cross_platform(p),
            "orchestration": self._measure_orchestration(p),
            "efficiency": self._measure_efficiency(p),
            "timestamp": datetime.now().isoformat(),
            "overall_alignment": 0  # calculated below
        }

        # Calculate overall alignment
        scores["overall_alignment"] = (
            scores["autonomy"] + scores["cross_platform"] +
            scores["orchestration"] + scores["efficiency"]
        ) / 4

        return scores

    def _measure_autonomy(self, platform) -> float:
        """Measure autonomy (0-100)"""
        # Check:
        # - Does platform auto-detect runtime?
        # - Do services self-start?
        # - Does queue-worker run autonomously?
        # - Does PM make decisions without override?

        score = 0
        if platform.get_runtime_strategy():
            score += 25
        if self._check_services_auto_start():
            score += 25
        if self._check_queue_worker_autonomous():
            score += 25
        if self._check_pm_autonomous():
            score += 25

        return score

    def _measure_cross_platform(self, platform) -> float:
        """Measure cross-platform capability (0-100)"""
        score = 0

        # Check:
        # - Platform detection works?
        # - Path translation works?
        # - Commands build correctly?
        # - Services install on this platform?

        if platform.get_path_translator():
            score += 25
        if platform.get_command_builder():
            score += 25
        if platform.get_service_manager():
            score += 25
        if self._check_platform_documentation():
            score += 25

        return score

    def _measure_orchestration(self, platform) -> float:
        """Measure self-orchestration (0-100)"""
        # Check:
        # - Does queue-worker route intelligently?
        # - Does PM select best model?
        # - Does system handle failures?
        # - Does system optimize priority?

        score = 0
        if self._check_intelligent_routing():
            score += 25
        if self._check_model_selection():
            score += 25
        if self._check_failure_handling():
            score += 25
        if self._check_priority_optimization():
            score += 25

        return score

    def _measure_efficiency(self, platform) -> float:
        """Measure multi-AI efficiency (0-100 scale = % of naive cost)"""
        # Check:
        # - Is batch API being used?
        # - Is prompt caching configured?
        # - Are models selected optimally?
        # - What's the actual cost efficiency?

        naive_cost = self._get_naive_cost()  # All tasks with Sonnet
        actual_cost = self._get_actual_cost()  # Current model mix

        if naive_cost > 0:
            efficiency = (actual_cost / naive_cost) * 100
            # Return score where lower = better (reversed)
            # Target is 40, so 40 = 100 score, 100 = 40 score
            return max(0, min(100, 100 - (efficiency - 40)))

        return 0

    # Stub methods (implement based on actual system state)
    def _check_services_auto_start(self) -> bool:
        return False  # Check if services auto-start

    def _check_queue_worker_autonomous(self) -> bool:
        return False  # Check if queue-worker runs without supervision

    def _check_pm_autonomous(self) -> bool:
        return False  # Check if PM makes decisions independently

    def _check_platform_documentation(self) -> bool:
        return False  # Check if docs cover all platforms

    def _check_intelligent_routing(self) -> bool:
        return False  # Check if routing is intelligent

    def _check_model_selection(self) -> bool:
        return False  # Check if models selected optimally

    def _check_failure_handling(self) -> bool:
        return False  # Check if failures handled gracefully

    def _check_priority_optimization(self) -> bool:
        return False  # Check if priorities optimized

    def _get_naive_cost(self) -> float:
        return 1.0  # Baseline cost (all Sonnet)

    def _get_actual_cost(self) -> float:
        return 0.4  # Current cost efficiency

    def save_progress(self, scores: dict):
        """Save scores to progress file"""
        self.progress["scores"].append(scores)
        self.progress["last_check"] = datetime.now().isoformat()

        self.PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.PROGRESS_FILE, 'w') as f:
            json.dump(self.progress, f, indent=2)

    def print_report(self, scores: dict):
        """Print alignment report"""
        print("\n" + "=" * 60)
        print("CENTRAL MOTIVE STATE - DAILY ALIGNMENT REPORT")
        print("=" * 60)
        print(f"Date: {scores['timestamp']}")
        print()

        pillars = {
            "autonomy": ("AUTONOMY", scores["autonomy"]),
            "cross_platform": ("CROSS-PLATFORM", scores["cross_platform"]),
            "orchestration": ("SELF-ORCHESTRATING", scores["orchestration"]),
            "efficiency": ("MULTI-AI EFFICIENCY", scores["efficiency"])
        }

        for key, (name, score) in pillars.items():
            bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
            status = "✓" if score >= 80 else "⚠" if score >= 60 else "✗"
            print(f"{status} {name:20} {bar} {score:3.0f}/100")

        print()
        print(f"OVERALL ALIGNMENT: {scores['overall_alignment']:.0f}/100")
        print("=" * 60)
        print()

        # Recommendations
        print("ALIGNMENT GUIDANCE:")
        if scores["autonomy"] < 80:
            print("  → Autonomy needs work. Prioritize self-healing infrastructure.")
        if scores["cross_platform"] < 80:
            print("  → Cross-platform support incomplete. Extend platform detection.")
        if scores["orchestration"] < 80:
            print("  → Self-orchestration needs improvement. Enhance PM decision-making.")
        if scores["efficiency"] > 60:  # Higher = less efficient
            print("  → Efficiency can be improved. Implement batch API + caching.")

        print()


def main():
    checker = MotiveStateChecker()
    scores = checker.check_alignment()
    checker.save_progress(scores)
    checker.print_report(scores)


if __name__ == "__main__":
    main()
```

---

## Part 3: Template for Daily Workorders

Create recurring daily workorder template: **`workorders/recurring/daily-motive-state-check.md.template`**

```markdown
# Daily: Motive State Alignment Check

**Frequency:** Daily
**Duration:** 10-15 minutes
**Owner:** Daily reviewer (human or automated)

---

## Today's Motive State Check

### Step 1: Run Alignment Script

```bash
python3 bin/check_motive_alignment.py
```

This generates a report showing:
- Autonomy Score
- Cross-Platform Score
- Orchestration Score
- Efficiency Score
- Overall Alignment

### Step 2: Review Today's Work

Questions to answer:

1. **What did we ship today?**
   - [List completed tasks]

2. **Does it move toward motive state?**
   - Autonomy? [Y/N]
   - Cross-Platform? [Y/N]
   - Self-Orchestrating? [Y/N]
   - Multi-AI Efficiency? [Y/N]

3. **What's the biggest gap right now?**
   - [Lowest-scoring pillar]
   - [Why is it low?]

4. **What should we prioritize next?**
   - [Suggested work based on gaps]

### Step 3: Decide Next Move

Using the Decision Rubric from MOTIVE_STATE.md:

| Work Item | Autonomy | Cross-Platform | Orchestration | Multi-AI | Decision |
|-----------|----------|---|---|---|---|
| [item 1] | Y/N | Y/N | Y/N | Y/N | ALIGNED / DISTRACTION |
| [item 2] | Y/N | Y/N | Y/N | Y/N | ALIGNED / DISTRACTION |
| [item 3] | Y/N | Y/N | Y/N | Y/N | ALIGNED / DISTRACTION |

### Step 4: Document & Commit

Update `logs/motive_state_progress.json` and commit with message:

```
chore: Daily motive state alignment check

Autonomy: XX/100
Cross-Platform: XX/100
Orchestration: XX/100
Efficiency: XX/100

Overall Alignment: XX/100

Biggest Gap: [pillar]
Next Priority: [work item]
```

---

## Success Criteria

- [ ] Alignment script runs without errors
- [ ] All four pillars measured
- [ ] Report clearly shows which pillar needs work
- [ ] Team can see alignment trend over time
- [ ] Tomorrow's priority clear from today's report
- [ ] Progress file updated

```

---

## Part 4: Metrics File Structure

Create: **`logs/motive_state_progress.json`**

```json
{
  "motive_state": "Autonomous, Cross-Platform, Self-Orchestrating Multi-AI System",
  "started": "2026-02-28T18:00:00Z",
  "last_update": "2026-02-28T18:00:00Z",
  "scores": [
    {
      "timestamp": "2026-02-28T18:00:00Z",
      "autonomy": 45,
      "cross_platform": 60,
      "orchestration": 35,
      "efficiency": 75,
      "overall_alignment": 53.75,
      "biggest_gap": "orchestration",
      "next_priority": "Implement intelligent model routing in PM"
    }
  ],
  "targets": {
    "autonomy": 95,
    "cross_platform": 100,
    "orchestration": 90,
    "efficiency": 40
  }
}
```

---

## Integration with Daily Workflow

This becomes part of your daily routine:

```
8:00 AM   - Start day
          - Run: python3 bin/check_motive_alignment.py
          - Review: What's misaligned?
          - Decide: What's the top priority?

9:00 AM   - Create/assign work
          - Use Decision Rubric: Is this aligned?
          - If aligned: Assign to agent
          - If distraction: Deprioritize

5:00 PM   - End of day
          - Review: Did we move alignment forward?
          - Update: motive_state_progress.json
          - Commit: Daily motive state check
          - Tomorrow: What's the next priority?
```

---

## Verification Checklist

- [ ] Created MOTIVE_STATE.md with clear definition
- [ ] Created check_motive_alignment.py script
- [ ] Script measures all four pillars
- [ ] Created daily workorder template
- [ ] Created metrics tracking JSON
- [ ] Integrated with daily workflow
- [ ] Team can understand motive state
- [ ] Decision rubric is clear and usable
- [ ] Progress is trackable over time
- [ ] Tomorrow's priorities clear from today's report

---

## Commit

```
feat: Create daily motive-state alignment system

- MOTIVE_STATE.md: Central guiding principle
- check_motive_alignment.py: Daily measurement script
- Daily workorder template: Recurring alignment check
- Metrics tracking: 4-pillar scoring system
- Decision rubric: Guide for aligning work
- Integrated into daily workflow

Central Motive State:
"Autonomous, Cross-Platform, Self-Orchestrating Multi-AI System"

This system allows daily verification that we're moving toward our vision.
```

START
reading repo structure
checking existing bin scripts and test patterns
creating docs/MOTIVE_STATE.md
creating bin/check_motive_alignment.py
creating workorders/recurring/daily-motive-state-check.md.template
creating logs/motive_state_progress.json
writing tests for motive state checker
all files created, verifying
COMPLETE


--- Agent Log ---
Invoking: /home/davey/.local/bin/claude --dangerously-skip-permissions --model opus -p - (cwd: /opt, repo: /opt/clones/opus/platform_13-create_daily_motive_state_wo-1773187532/repo)
All done. Here's what was created:

**5 files in the repo:**

1. **`docs/MOTIVE_STATE.md`** — Central Motive State reference with four pillars (Autonomous, Cross-Platform, Self-Orchestrating, Multi-AI), daily alignment questions, decision rubric, and 90-day plan
2. **`bin/check_motive_alignment.py`** — Daily comparison script with `MotiveStateChecker` class that measures all four pillars by checking actual repo artifacts (queue-worker config, PM data, platform detection, agent configs, etc.), saves progress, and prints a formatted report
3. **`workorders/recurring/daily-motive-state-check.md.template`** — Recurring daily workorder template with 4 steps: run script, review work, decide next move, document & commit
4. **`logs/motive_state_progress.json`** — Initial metrics tracking file with baseline scores and targets
5. **`tests/test_motive_state.py`** — 28 tests covering all components: file existence, structure, script validity, checker class behavior (scores, ranges, averages, save/load), template content, and progress file format

[INFO] Agent execution completed
[INFO] Log: /opt/csc/ops/logs/opus_1773187533.log
