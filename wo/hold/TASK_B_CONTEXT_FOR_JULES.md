# TASK B: Workorder Architecture - Context for Jules

## Quick Start

**Repository**: https://github.com/daveylongshaft/csc.git (private)

**Clone**:
```bash
git clone --recursive https://github.com/daveylongshaft/csc.git
cd csc
```

**GitHub Authentication** (if prompted):
```
Use your personal access token (PAT) configured locally or in .env
```

---

## Your Task

**See**: `TASK_B_WORKORDER_ARCHITECTURE_REDESIGN.md`

**In Summary**:

Design a workorder system for multi-system autonomous agents that:
- Keeps workorders in ONE known location (pooling/buffering)
- Uses ready → wip → done workflow
- Agents independently **claim** work (clear, atomic, replicatable mechanism)
- Agents only read and append (no file movement)
- Works across distributed servers

**Answer These 5 Questions**:
1. Where do workorders live permanently?
2. How do agents claim work ("I got this one")?
3. What are the state transitions?
4. How do distributed agents stay in sync?
5. How are agents identified across systems?

**Then Provide**:
- Implementation spec
- State transition diagram
- Claiming protocol (step-by-step)
- Edge case handling

**Key Constraints**:
- Claiming must be atomic (no race conditions)
- Claiming must be obvious and visible
- Must work across independent servers
- No central bottleneck

**When Done**:
- Push architecture document to repository
- Or send back for review
