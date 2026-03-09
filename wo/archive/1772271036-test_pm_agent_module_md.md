# Test PM Agent Module - Comprehensive Validation

## Objective

Verify that the PM Agent Module (implemented in previous WO) correctly orchestrates workorder processing with intelligent prioritization, agent selection, batching, self-healing, and cascading logic.

## Prerequisites

✅ PM Agent Module implementation MUST be complete in `packages/csc-service/csc_service/infra/pm.py`

## Test Categories

### 1. Priority Cascade Logic

**Test 1.1: Infrastructure Priority**
- Create 5 workorders: 1 infra, 1 bug, 1 test fix, 1 doc, 1 feature
- Verify PM processes infra first (regardless of creation order)
- Check PM journal: logs "PRIORITY: infrastructure"

**Test 1.2: Bug Fix Priority**
- Create: 2 bug fixes, 2 test fixes, 1 doc
- Verify PM processes both bugs before any tests/docs
- Check cascading: After infra done, bugs get priority

**Test 1.3: Test Fix Auto-Trigger**
- Create: 1 infrastructure WO
- After infra completes, verify PM auto-creates test-fix WOs
- Check: PM journal logs "CASCADE: infra complete → test-fix regen"

**Test 1.4: Hold Feature WOs**
- Create: 3 features + 1 bug + 1 infra
- Verify PM holds features until infra/bug stabilize
- Features should be in "hold" state, not "ready"

### 2. Agent Selection Cascade

**Test 2.1: Gemini-3-Pro First**
- Create coding WO (no special requirements)
- Verify PM selects gemini-3-pro
- Check journal: "AGENT_SELECTION: gemini-3-pro (coding, primary)"

**Test 2.2: Gemini-2.5-Pro Fallback**
- Create: Set GEMINI_3_PRO_QUOTA=0 (exhausted)
- Create coding WO
- Verify PM falls back to gemini-2.5-pro
- Check journal: "FALLBACK: gemini-3-pro exhausted → gemini-2.5-pro"

**Test 2.3: Haiku Batch Caching**
- Create: 5 identical documentation WOs
- Verify PM batches them as 1 haiku job with prompt caching
- Check performance: Single haiku call vs 5 separate calls

**Test 2.4: Opus Self-Repair**
- Create: WO that will fail (intentionally broken)
- Assign to wrong agent (gemini for complex logic task)
- Verify fails 3+ times
- PM should spawn opus for self-diagnosis
- Check journal: "FALLBACK: persistent failure → opus debug agent"

### 3. Batching Logic

**Test 3.1: Same-Type Grouping**
- Create: 5 test-fix WOs, 3 doc WOs, 2 bug WOs
- Verify PM groups:
  - All 5 test-fixes together
  - All 3 docs together
  - 2 bugs separate (less than threshold)
- Check journal shows batching decisions

**Test 3.2: Anthropic Prompt Caching**
- Create: 3 haiku batches (same agent, same context)
- Verify second batch uses cached prompt (faster, cheaper)
- Compare tokens: Batch 1 (full) vs Batch 2 (cached)
- Expected: 70%+ token savings on cached batch

**Test 3.3: Gemini Non-Batch**
- Create: 5 gemini WOs
- Verify PM runs them one-at-a-time (no batch API)
- Check journal: "GEMINI_NO_BATCH: running serial due to API limits"

### 4. API Key Rotation

**Test 4.1: Key Exhaustion Detection**
- Set up 2 API keys with low quotas in .env
- Create: 10 WOs that will exhaust KEY_1
- Verify PM detects quota hit
- Rotates to KEY_2
- Check journal: "KEY_ROTATION: KEY_1 exhausted (quota=1000) → KEY_2"

**Test 4.2: Key Performance Tracking**
- Create: Mix of WOs (some fast, some slow)
- Verify PM tracks completion rate per key
- Rate keys: Which key completes fastest?
- Check PM metrics: "KEY_1: 95% completion rate, KEY_2: 87%"

**Test 4.3: Fallback Chain**
- Exhaust: gemini-3-pro → gemini-2.5-pro → gemini-3-flash → haiku
- Create: WO every time quotas hit
- Verify PM follows fallback order
- Final fallback should be haiku with caching

### 5. Self-Healing Capability

**Test 5.1: Opus Self-Fix**
- Intentionally break PM logic (e.g., bad priority function)
- Create: WO that fails due to broken PM
- Verify: Opus spawns, reads PM source code
- Opus fixes the broken logic
- PM resumes normal operation
- Check: Fixed code committed, journal logs repair

**Test 5.2: Haiku Debug Report**
- Create: WO that fails consistently (3+ attempts, different agents)
- Verify: Haiku spawns, examines logs
- Haiku generates diagnostic report
- Output: "Root cause: Invalid file path (cross-platform issue)"
- Verify: Haiku creates resolution WO with findings

### 6. Cascading Logic

**Test 6.1: Infra → Bug Cascade**
- Create: 1 infrastructure WO
- Complete it (agent finishes, marks COMPLETE)
- Verify: PM auto-generates dependent bug-fix WOs
- Check journal: "CASCADE_DETECTED: infra complete → creating 3 bug-fix WOs"

**Test 6.2: Bug → Test Cascade**
- After infra/bugs complete
- Verify: PM triggers test-runner to regenerate test-fix WOs
- Check: New test-fix WOs appear in ready/
- Journal: "CASCADE_TRIGGER: test-runner invoked"

**Test 6.3: Code → Docstring Regen**
- Create: Code modification WO
- After completion
- Verify: PM triggers docstring/map regeneration
- Check: tools/ directory updated with new maps
- Journal: "POST_PROCESS: refresh-maps invoked"

### 7. PM Journal & Monitoring

**Test 7.1: Decision Logging**
- Run PM through full cycle (10+ WOs)
- Verify journal contains:
  - Priority decisions (why order chosen)
  - Agent selection rationale
  - Batching groupings
  - Cascading triggers
  - Self-heal events

**Test 7.2: Performance Metrics**
- Check PM outputs:
  - Agent completion rates (%)
  - Average time per WO (seconds)
  - Cost per agent type
  - API key depletion rates
  - Self-heal invocations

**Test 7.3: Audit Trail**
- Verify: Every PM decision traceable
- Check: Timestamps, agent assignments, rationale logged
- Ensure: No silent decisions (all logged)

### 8. Error Handling & Recovery

**Test 8.1: Queue Corruption Recovery**
- Corrupt agents/*/queue/in/ files
- Verify: PM detects, cleans up
- WOs are re-queued safely

**Test 8.2: Agent Crash Handling**
- Create: WO assigned to gemini
- Mid-execution, kill gemini process
- Verify: PM detects timeout, re-queues
- Retries with fallback agent

**Test 8.3: API Error Handling**
- Simulate API errors: 429 (rate limit), 503 (service down)
- Verify: PM backs off, retries exponentially
- Doesn't spam API on errors

### 9. Integration Tests

**Test 9.1: Queue-Worker Integration**
- Verify: PM works correctly with queue-worker
- WOs flow: ready/ → (PM assigns) → agents/ → done/
- No race conditions or deadlocks

**Test 9.2: Path-Protection Integration**
- Create: WO that modifies protected files
- Verify: PM routes to opus (harder tasks)
- PR creation flows correctly
- AI reviewer approves/rejects as expected

**Test 9.3: End-to-End Flow**
- Create: 20 mixed workorders (all types)
- Let PM orchestrate full lifecycle
- All complete successfully
- Journal shows proper cascading/prioritization

## Testing Procedure

```bash
# 1. Start fresh PM instance
pm.setup(CSC_ROOT)

# 2. Create test workorders
wo add test-1.md : "Test infrastructure change"
wo add test-2.md : "Test bug fix"
wo add test-3.md : "Test documentation"
# ... etc

# 3. Run PM through cycles
# (via queue-worker or direct API)
python -m csc_service.infra.pm --test-mode

# 4. Verify results
# Check pm-execution-journal.md
# Check agent assignments
# Verify WO movements: ready → WIP → done

# 5. Validate metrics
pm.get_performance_metrics()
pm.get_api_key_status()
pm.get_self_heal_log()
```

## Success Criteria

- [X] All 9 test categories pass
- [X] No unhandled exceptions
- [X] Priority cascade works correctly
- [X] Agent selection follows fallback chain
- [X] Batching reduces API calls
- [X] API key rotation works seamlessly
- [X] Self-healing fixes PM bugs
- [X] Cascading logic triggers correctly
- [X] All decisions logged with rationale
- [X] Performance metrics accurate
- [X] Integration with queue-worker smooth
- [X] No race conditions or deadlocks
- [X] Error handling robust
- [X] Documentation up to date

## Known Risks

⚠️ **Self-Heal Risk:** Opus modifying PM code could introduce bugs
- Mitigation: Test self-heal separately first
- Limit opus write access to pm.py only

⚠️ **API Cost Risk:** Testing many cycles could consume quota
- Mitigation: Use --test-mode with mock agents
- Use limited quotas to force fallbacks

⚠️ **Cascading Complexity:** Hard to predict all cascade scenarios
- Mitigation: Test each cascade independently first
- Then test combinations

## Timeline

- Setup & prep: 5 min
- Run tests: 20-30 min (depending on queue throughput)
- Verify & validate: 10-15 min
- Fix issues (if any): 10-20 min
- **Total: ~45-75 min** for full validation
