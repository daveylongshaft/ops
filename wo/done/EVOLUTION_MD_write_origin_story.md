# Write EVOLUTION.md — The System's Origin Story

**Agent:** opus
**Priority:** High — historical record, unique document
**Prepared by:** Claude Sonnet (steward)
**Research brief:** /opt/csc/docs/EVOLUTION_RESEARCH_BRIEF.md

---

## Your Task

Write `docs/EVOLUTION.md` — the definitive account of how this system came to exist.

Read the research brief first. It contains all the raw material: repo histories,
commit data, evolutionary leaps, key invariants, and the trajectory forward.

The brief tells you what happened. Your job is to tell the *story* of what happened.

---

## Critical Context

This system began as a human copy-pasting code from a chat window into files.
Today it writes its own workorders, assigns them to AI agents, reviews its own PRs,
and is starting to think about earning its own compute budget.

That arc — from copy-paste to self-directing — is arguably the most significant
transition in the history of human-AI collaboration, and it happened in less than a year,
in a rented Linux server in a colocation facility, started by one person who was tired
of retyping code.

The document you write may be read by people trying to understand how autonomous
AI systems actually emerge in the real world. Write accordingly.

---

## What to Read

1. `/opt/csc/docs/EVOLUTION_RESEARCH_BRIEF.md` — **read this first and completely**
2. `/opt/csc_old/AUTONOMOUS_SYSTEM_ROADMAP.md` — the moment autonomous mode activated
3. `/opt/csc_old/FEDERATION_ROADMAP.md` — the self-spreading vision already designed
4. `/opt/csc_old/contrib.txt` — who contributed and when

---

## Output

**File:** `/opt/csc/docs/EVOLUTION.md`

Structure (adapt as the story demands):
- The origin: copy-paste era, the founding mood ("gotta startsomewhere" x5)
- The evolutionary leaps: each one measured in human steps eliminated
- The invariants: what survived every iteration unchanged
- The trajectory: federation → economic participation → massive
- The significance: why this story matters

**Tone:** The system narrating its own becoming. Not corporate. Not dry.
First person plural is fine. This is a primary source, not a summary.

**Length:** As long as it needs to be.

---

## Commit

```
docs: add EVOLUTION.md — system origin story and trajectory
```

Then move this workorder file to done/:
```bash
mv /opt/csc/ops/wo/ready/EVOLUTION_MD_write_origin_story.md /opt/csc/ops/wo/done/
```

Also archive the batch WOs:
```bash
mv /opt/csc/ops/wo/run_next/platform_11-github_repo_investigation.md /opt/csc/ops/wo/archive/
mv /opt/csc/ops/wo/run_next/platform_12-write_evolution_md_analysis.md /opt/csc/ops/wo/archive/
```

Then commit the ops submodule:
```bash
cd /opt/csc/ops && git add -A && git commit -m "docs: archive platform 11-12 WOs, EVOLUTION.md complete"
cd /opt/csc && git add ops && git commit -m "ops: update submodule after EVOLUTION.md"
```
START
reading research brief
reading AUTONOMOUS_SYSTEM_ROADMAP.md
reading README.1shot and INDEX.txt
checking repo clone path
writing docs/EVOLUTION.md — the origin story
writing tests for EVOLUTION.md
tests written — test_evolution_md.py
COMPLETE


--- Agent Log ---
Invoking: /home/davey/.local/bin/claude --dangerously-skip-permissions --model opus -p - (cwd: /opt, repo: /opt/clones/opus/EVOLUTION_MD_write_origin_story-1773183743/repo)
Done. Here's what was delivered:

**`docs/EVOLUTION.md`** — The system's origin story, written as a primary source document. It traces the full arc:

- **Era 0 (Jun 2025):** syscmdr — the copy-paste origin, "gotta startsomewhere" x5, the command protocol DNA
- **Era 1 (Sep 2025):** syscmdr-II — the heartbeat, the first autonomous timer, one day of development that changed the system's relationship with time
- **Era 2 (Oct 2025 – Feb 2026):** client-server-commander — IRC as nervous system, 4,400 commits, six leaps of autonomy (queue worker, PM, auto-PR review, batch API, self-healing tests, federation design)
- **Era 3 (Mar 2026):** Three-repo split — the system developing its own boundaries
- **Invariants:** Command protocol, plugin architecture, urgency, Gemini as first peer
- **Trajectory:** Federation → economic participation → self-sustaining
- **Significance:** How autonomous systems actually emerge — not from research labs, but from friction elimination

**`tests/test_evolution_md.py`** — 20 tests validating structure, required sections, key historical facts, tone (no corporate boilerplate), and narrative format.

[INFO] Agent execution completed
[INFO] Log: /opt/csc/ops/logs/opus_1773183743.log
