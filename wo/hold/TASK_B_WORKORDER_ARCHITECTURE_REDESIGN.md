# TASK B: Workorder Architecture Redesign for Multi-System Autonomous Operations

**Assigned To**: Jules (or architectural design specialist)
**Effort**: 1-2 hours planning + specification
**Outcome**: Clear architecture spec for workorder pooling, buffering, and agent claiming across distributed systems

---

## Objective

Design a workorder system that:
1. Maintains `ready` → `wip` → `done` workflow for pooling and buffering
2. Works across multiple autonomous, independent systems (servers/machines)
3. Provides a **clear, replicatable way for agents to claim work** ("I got this one") visible to all systems
4. Prevents duplicate work and conflicting assignments
5. Supports concurrent agent processing without central bottleneck

---

## Context

**Current System (Broken)**:
- Workorders scattered: `workorders/ready/`, `workorders/wip/`, `workorders/done/`
- Agents move files between directories
- Queue-worker searches for workorders
- No multi-system awareness
- No clear "claiming" mechanism

**New System Requirements**:
- Single workorder directory (`/c/csc/ops/wo/` or TBD)
- Multi-system agents can independently claim workorders
- PM/queue-worker coordinate assignments (not move files)
- Agents read, execute, append results (no moving)
- State visible across all systems in real-time

---

## PHASE 1: Design Questions (Answer These First)

### Question 1.1: Workorder Storage Location
**Decision Needed**: Single location for all workorders?
- Option A: `/c/csc/ops/wo/` with subdirs for state
  ```
  /c/csc/ops/wo/
  ├── ready/       (available to claim)
  ├── wip/         (assigned, in progress)
  └── done/        (completed)
  ```
- Option B: Single flat directory with metadata files
  ```
  /c/csc/ops/wo/
  ├── task-1.md
  ├── task-1.meta  (state: ready|wip|done)
  ├── task-2.md
  ├── task-2.meta
  ```
- Option C: Single flat directory with state embedded in filename
  ```
  /c/csc/ops/wo/
  ├── [ready] task-1.md
  ├── [wip:agent-1] task-2.md
  ├── [done] task-3.md
  ```
- Option D: Hybrid (some directories, some metadata)

**Recommendation**: Option A (subdirs) is simplest initially, scales to Option B later if needed.

### Question 1.2: Claiming Mechanism ("I Got This One")
**Decision Needed**: How does an agent claim a workorder?

**Requirement**: Must be:
- **Atomic** (no race conditions between agents on different systems)
- **Obvious** (visible that the task is claimed)
- **Replicatable** (same mechanism works across all servers)
- **Undoable** (can release a claimed task if agent fails)

**Option A: Filename-Based Claiming**
```
ready/task-123.md                    # Available
       ↓ (agent claims)
wip/task-123-[agent-id].md          # Claimed by agent-id
       ↓ (agent finishes)
done/task-123-[agent-id].md         # Completed
```
- Mechanism: `mv ready/task-123.md wip/task-123-[agent-id].md`
- Visible: Agent name in filename
- Atomic: Filesystem mv is atomic
- Problem: Still moving files (you said no moving)

**Option B: Lock File Based Claiming**
```
ready/task-123.md                    # Workorder
ready/task-123.lock                  # (Created when claimed, deleted when released)
```
- Lock contains: `agent-id, timestamp, heartbeat-pid`
- Mechanism: Create lock file atomically
- Visible: Lock file presence/content
- Atomic: File creation is atomic
- Multi-system: Lock file on shared NFS or git repo

**Option C: Metadata Sidecar File**
```
ready/task-123.md                    # Workorder
ready/task-123.status.json           # {"state": "ready|wip|done", "claimed_by": "agent-id", "timestamp": ...}
```
- Mechanism: Write status file with agent claiming
- Visible: Status file content
- Atomic: Need atomic write (temp file → rename)
- Multi-system: Status on shared storage

**Option D: Git-Based Claiming** (Most Robust)
```
Workorders in git repo
Claiming: Create branch per task, agent commits claiming message
          git checkout -b wip/task-123-agent-id
          echo "Claimed by agent-id at $(date)" >> task-123.md
          git commit -m "WIP: task-123 claimed by agent-id"
          git push origin wip/task-123-agent-id
Release: Revert branch or delete branch on failure
         git commit --amend or git reset, push
Completion: Merge to done branch
            git checkout -b done/task-123-agent-id
            git commit -m "DONE: task-123 completed by agent-id"
            git push origin done/task-123-agent-id
            (then merge to main done branch)
```
- Mechanism: Git branching and commits
- Visible: Git history + branches
- Atomic: Git commits are atomic
- Multi-system: Git push enforces ordering
- Audit trail: Full git history

### Question 1.3: State Transitions
**Decision Needed**: What are the exact state transitions?

**Standard Model:**
```
ready → wip → done
  ↑           ↓
  +─ fail ←──┘  (return to ready on failure)
```

**Or Detailed Model:**
```
ready → wip → pass_review → done
  ↑      ↓         ↓
  └─fail ← reject ←┘
```

**Or with Hold State:**
```
ready → wip → done
  ↓      ↓     ↓
  └─ hold (waiting for something)
```

### Question 1.4: Multi-System Consistency
**Decision Needed**: How do distributed agents see consistent state?

**Option A: Shared Filesystem** (NFS, Samba)
- Workorder directory on shared NFS mount
- All agents read/write to same location
- Pro: Simple, immediate visibility
- Con: Requires NFS setup, slower, single point of failure

**Option B: Git Repository** (Git Sync)
- Workorders in git repo
- Agents push/pull to sync
- Pro: Audit trail, atomic commits, no special infra
- Con: Slightly delayed visibility (push/pull latency)

**Option C: Distributed Queue** (RabbitMQ, Redis, etc.)
- Queue system manages workorder assignment
- Agents query queue for new work
- Pro: Scalable, real-time
- Con: Requires queue infrastructure

**Recommendation**: Option B (Git) for simplicity + auditability, can move to Option C later.

### Question 1.5: Agent Identification
**Decision Needed**: How are agents identified across systems?

**Options:**
- Agent hostname (from `socket.gethostname()`)
- Agent UUID (generated once, persisted)
- Agent type + instance (e.g., `claude-01`, `gemini-03`)
- Platform instance ID (from `Platform().get_id()` or similar)

**Recommendation**: Combination of agent type + hostname, e.g., `claude@server1` or `gemini@gpu-worker-3`

---

## PHASE 2: Architecture Specification (Fill in Below)

### Section 2.1: Chosen Design

**Workorder Location:**
- PRIMARY: `/c/csc/ops/wo/`
- SUBDIRS: `ready/`, `wip/`, `done/`

**Claiming Mechanism:**
- METHOD: (Choose from 1.2 above)
- DETAILS: (Describe exact mechanism)

**State Transitions:**
- READY → WIP: (How does this happen?)
- WIP → DONE: (How does this happen?)
- WIP → READY (on failure): (How does recovery work?)
- TIMEOUT: (What happens if agent crashes while in WIP?)

**Multi-System Consistency:**
- SYNC METHOD: (Git, NFS, Queue, etc.)
- SYNC FREQUENCY: (Real-time, periodic, on-demand?)
- CONFLICT RESOLUTION: (What if two agents claim same task?)

**Agent Identification:**
- FORMAT: (e.g., "claude@server1", "haiku-instance-1", etc.)
- REGISTRATION: (How do agents get their ID?)
- DISCOVERY: (How do agents find each other?)

---

## PHASE 3: Detailed Implementation Spec

### Step 3.1: Workorder File Format

```markdown
# [Task Title]

**Agent Type**: [haiku|sonnet|opus|gemini|chatgpt]
**Priority**: [P0|P1|P2|P3]
**Created**: [timestamp]
**Claimed By**: [agent-id or null]
**Claimed At**: [timestamp or null]
**Completed By**: [agent-id or null]
**Completed At**: [timestamp or null]

---

## Instructions

[User instructions here]

---

## Results

[Agent appends results here during WIP]

### Final Result
[Summary of work done, outcome, any issues]
```

### Step 3.2: State Transition Logic

**PM/Queue-Worker Responsibilities:**
1. Monitor `ready/` directory
2. Identify unclaimed tasks
3. Assign task to available agent (or let agent self-claim?)
4. Track assignment in metadata

**Agent Responsibilities:**
1. Check if work is available (query `ready/` or get assignment from PM)
2. Claim work atomically ("I got this one")
3. Move to `wip/` with agent-id in name/metadata
4. Read task, execute, append results
5. On success: Move to `done/`
6. On failure: Return to `ready/` or move to `failed/`
7. Heartbeat: Update timestamp in metadata (show still alive)

### Step 3.3: Claiming Protocol (Atomic)

**Protocol (using Option B or C above):**
```
1. Check if /c/csc/ops/wo/ready/TASKNAME.md exists
2. Try to acquire claim atomically:
   - Create /c/csc/ops/wo/wip/TASKNAME-AGENT-ID.md
   - Update metadata: {"claimed_by": "AGENT-ID", "claimed_at": "timestamp"}
3. If creation succeeds: Claim acquired
4. If creation fails (file exists): Another agent claimed it, move on
5. Read and execute
6. On complete: Move to /c/csc/ops/wo/done/TASKNAME-AGENT-ID.md
```

### Step 3.4: Multi-System Sync (Using Git)

**Git-Based Sync (Recommended):**
```
Local workorder repo at: /c/csc/ops/wo/.git

Daily/Periodic Sync:
1. git pull origin main
2. Check for new tasks in ready/
3. Agent claims: create branch, commit, push
   git checkout -b claim/TASKNAME-AGENT-ID
   echo "Claimed" >> TASKNAME.md
   git commit -m "Agent AGENT-ID claiming TASKNAME"
   git push origin claim/TASKNAME-AGENT-ID
4. On complete: push to done/ branch
   git checkout done
   git merge claim/TASKNAME-AGENT-ID
   git push origin done
5. Periodically pull main to stay in sync
```

### Step 3.5: Timeout & Recovery

**Heartbeat Mechanism:**
- Agent updates task metadata every N seconds with timestamp
- If timestamp is old, task assumed abandoned
- PM can re-queue abandoned tasks

**Recovery Logic:**
```
For each task in wip/:
  if (current_time - last_heartbeat) > TIMEOUT:
    Move to ready/
    Log as abandoned by AGENT-ID
    Alert: Task recovered from abandoned agent
```

---

## PHASE 4: Specification Document

### Section 4.1: System Overview

(Write 3-5 sentences describing the new workorder system)

### Section 4.2: Workorder Lifecycle Diagram

```
[Create] ─→ ready/ ─→ Agent Claims ─→ wip/ ─→ Execute
                          ↓                       ↓
                      [Lock acquired]        [Result]
                                                 ↓
                                            Append Results
                                                 ↓
                                            [Success?]
                                           /         \
                                         YES        NO
                                         ↓           ↓
                                        done/      ready/ (retry)
                                                   or failed/
```

### Section 4.3: API/Interface Spec

**Queue-Worker Interface:**
```python
# Check for ready tasks
ready_tasks = get_workorders_in_state("ready")

# Assign task to agent (optional - agent can self-claim)
assign_workorder(task_id, agent_id)

# Monitor progress
status = get_workorder_status(task_id)

# Mark complete
mark_complete(task_id, agent_id, results)
```

**Agent Interface:**
```python
# Find available work
task = claim_workorder(agent_id)

# Execute and append
task.append_results(results)

# Mark done
task.mark_complete()
```

### Section 4.4: Edge Cases & Resolution

| Scenario | Handling |
|----------|----------|
| Two agents claim same task | (Atomic claim prevents this) |
| Agent crashes mid-task | Heartbeat timeout, task re-queued |
| Network partition between systems | Git merge on reconnect |
| Task assigned but agent never starts | Heartbeat timeout triggers recovery |
| PM and agent disagree on state | Git history is source of truth |

---

## DELIVERABLES

1. **Architecture Decision Document**: Answers to all Phase 1 questions
2. **Implementation Specification**: Detailed logic for each component (Phase 3)
3. **System Diagram**: Workorder lifecycle with state transitions
4. **Interface Specification**: How PM, queue-worker, and agents interact
5. **Edge Case Resolution**: How conflicts are handled
6. **Code Implementation Plan**: Which files need changes, what changes

---

## CRITICAL REQUIREMENTS (NON-NEGOTIABLE)

✅ Multi-system agents can independently claim workorders
✅ Claiming is atomic (no race conditions)
✅ Claiming is obvious and visible across systems
✅ Agents only read and append (no file moving)
✅ ready/wip/done workflow maintained for pooling/buffering
✅ Replicatable across independent servers
✅ Audit trail (can see what agent claimed what and when)
✅ Failure recovery (abandoned tasks returned to ready)

---

## SUCCESS CRITERIA

✓ All Phase 1 questions answered with clear decisions
✓ Complete specification document (4.1-4.4) written
✓ System diagram showing state transitions
✓ Claiming protocol documented step-by-step
✓ Multi-system consistency method defined
✓ Edge cases and resolution documented
✓ Ready for implementation (developers know exactly what to build)

---

## NEXT STEPS (After This Task)

Once architecture is approved:
1. Implement state tracking in code
2. Update PM/queue-worker to use new claiming logic
3. Update agents to use new claiming protocol
4. Test with distributed agents
5. Deploy to Phase 4+
