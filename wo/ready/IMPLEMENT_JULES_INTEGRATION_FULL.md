---
urgency: P2
tags: infrastructure,integration,external-contractor,automation
requires: [git, python3, npm, nodejs]
---

# Implement: Jules Integration (Full Workorder Assignment + Auto Plan Review)

## Objective

Integrate Google's Jules AI coding agent as a workorder assignment option. PM autonomously assigns workorders to Jules when it has capacity and the work is suitable. Jules creates pull requests; plan-review agent approves/denies plans automatically.

## Specification

Full technical spec at: `/c/csc/JULIUS_INTEGRATION_WORKORDER_SPEC.md`

Quick summary:
- Jules becomes assignable like `workorders assign 1 julius`
- PM decides when to use Jules (capacity + task suitability)
- Plans auto-approved (plan-review agent handles approval)
- Results returned as GitHub PRs
- Fully automated workflow

## Implementation Steps

### Phase 1: Jules CLI & Authentication

1. Install Jules CLI globally:
   ```bash
   npm install -g @google/julius
   julius login  # Opens browser for OAuth
   ```

2. Store API key:
   ```bash
   mkdir -p config/
   echo "YOUR_API_KEY_HERE" > config/julius_api_key
   ```

3. Verify installation:
   ```bash
   julius version
   julius remote list  # Should return empty initially
   ```

### Phase 2: Jules Client Module

Create: `csc_service/clients/julius/`

**Structure:**
```
csc_service/clients/julius/
├── __init__.py
├── julius.py       # Main Jules client class
└── config.py       # Configuration loader
```

**Key Methods (julius.py):**
- `__init__(api_key_path, github_repo, auto_approve=True)`
- `submit_workorder(workorder_path, repo_url) → session_id`
- `check_status(session_id) → {'state': 'running'|'completed'|'failed'}`
- `get_results(session_id) → {'pr_url': '...', 'changes': [...]}`
- `cancel_session(session_id) → bool`

Use Jules CLI commands:
```bash
julius remote new --repo <repo> --prompt <prompt>  # Create
julius remote list --session <id>                   # Status
julius remote pull --session <id>                   # Results
```

### Phase 3: PM Enhancement

Update: `csc_service/infra/pm.py`

**Add methods:**
- `_is_julius_task(workorder) → bool` — Check if suitable (keywords: bug, fix, refactor, test, doc, feature)
- `julius_has_capacity() → bool` — Check active sessions < max (e.g., 3)
- `assign_to_julius(workorder)` — Create Jules session
- `monitor_julius_sessions()` — Poll status, retrieve results
- `_handle_julius_result(session_id, result)` — Create PR or integrate

**Update:**
- `run_cycle()` — Add Jules assignment logic alongside Sonnet/Haiku/Gemini

### Phase 4: Configuration

Update: `csc-service.json`

Add Jules section:
```json
{
  "julius": {
    "enabled": true,
    "api_key_path": "config/julius_api_key",
    "github_repo": "daveylongshaft/csc",
    "github_branch": "main",
    "max_concurrent_sessions": 3,
    "auto_approve_plans": true,
    "task_keywords": ["bug", "fix", "refactor", "test", "documentation", "feature"]
  }
}
```

Also create: `config/julius_api_key` (git-ignored, user-provided)

### Phase 5: Plan Review Agent

If not already set up (separate workorder exists), create:

`agents/plan-review/context/system.md` with approval criteria
`csc_service/infra/plan_review.py` with polling service
Wire into `pm.run_cycle()` to check plan decisions

### Phase 6: Testing

Create: `tests/test_julius_client.py`

**Unit tests:**
- Jules client initialization
- Session creation/status/results parsing
- Plan decision parsing

**Integration tests:**
- PM assigns workorder to Jules
- Jules session created + monitored
- Plan reviewed + approved/denied
- Results retrieved

**Regression tests:**
- Existing workorder flows unaffected
- PM still assigns to Sonnet/Haiku correctly
- No interference with pr-review or queue-worker

### Phase 7: Documentation

Update/create:
- `docs/library/pm.md` — Add Jules assignment workflow
- `docs/library/julius_integration.md` (new) — Architecture + curl examples
- `irc/CLAUDE.md` — Update workorder assignment section

## Files to Create/Modify

**Create:**
- `csc_service/clients/julius/__init__.py`
- `csc_service/clients/julius/julius.py`
- `csc_service/clients/julius/config.py`
- `config/julius_api_key` (git-ignored)
- `tests/test_julius_client.py`

**Modify:**
- `csc_service/infra/pm.py` (add Julius assignment + monitoring)
- `csc-service.json` (add Julius config)
- `docs/library/pm.md` or create new doc

## Code Standards (Important)

Follow CSC patterns:
- ✅ One class per file (class Julius in julius.py)
- ✅ Use Platform() for all paths (never hardcode)
- ✅ Inherit from Log for logging (`self.log()`)
- ✅ Type hints (Python 3.8+)
- ✅ Docstrings (module/class/method)
- ✅ No breaking changes (backward compatible)
- ✅ Tests runnable by test-runner

## Success Criteria

✅ `workorders assign 1 julius` works
✅ PM automatically assigns Julius-suitable work when capacity available
✅ Jules creates sessions via CLI
✅ Plan-review agent approves/denies plans autonomously
✅ PM monitors sessions + retrieves results
✅ Results → GitHub PRs
✅ Workorders flow ready → wip → done
✅ No regressions to existing systems
✅ All tests pass after commit
✅ Docs updated with Julius workflow

## Assumptions

- Jules CLI installed globally (`npm install -g @google/julius`)
- API key obtained and stored in `config/julius_api_key`
- GitHub repo configured (daveylongshaft/csc or user-specified)
- plan-review agent already set up (or created separately)

## Notes

- Julius is alpha (specs may change); code defensively
- Auto-approve plans is safe (PM made assignment decision)
- Max concurrent sessions recommended: 3-5
- If Julius fails, consider fallback to Sonnet

---

**Use your best engineering judgment on:**
- Exception handling for Julius CLI failures
- Session timeout/stale detection
- Fallback behavior if Julius API unavailable
- Result parsing (PR URL extraction, changes integration)
- Logging verbosity (debug vs production)

This is significant infrastructure work. Design it to scale, fail gracefully, and integrate seamlessly with existing PM logic.

READY FOR IMPLEMENTATION
