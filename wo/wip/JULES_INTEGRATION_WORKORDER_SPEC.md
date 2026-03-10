# Jules Integration: Workorder Assignment Option

## Overview

Jules becomes an **additional execution target** in the workorder assignment system, alongside sonnet, opus, haiku, gemini, chatgpt, etc.

**PM decides when to use Jules based on:**
- Jules has available capacity
- Workorder type matches Jules's strengths (code generation, bug fixing, refactoring, documentation)
- Jules can provide better outcomes than available local agents

---

## Integration Architecture

### 1. Jules as a "Backend" (Like Sonnet/Opus)

**Workorder Assignment Flow:**
```
prompts add "Fix bug in auth.py" : [content...]
↓
prompts list ready
↓
workorders assign 1 jules        ← NEW: Jules as valid assignment target
↓
pm.run_cycle() detects in queue  ← PM picks up
↓
Jules service spawns session     ← Executes work
↓
Results → Pull Request           ← Returns as PR
↓
prompts move done/               ← Mark complete
```

**CLI Usage:**
```bash
# Assign workorder to Jules
workorders assign 1 jules

# Or via AI command
AI 1 workorders assign 1 jules

# Check Jules status
agent status jules

# List workorders assigned to Jules
workorders list wip | grep jules
```

### 2. PM Integration

**PM's Decision Logic:**
```python
def run_cycle(self):
    """PM: Assign workorders to agents based on capacity & suitability."""

    ready_wos = self.get_ready_workorders()

    for wo in ready_wos:
        # Check if Jules should handle it
        if self.is_jules_suitable(wo) and self.jules_has_capacity():
            self.assign_to_jules(wo)
        elif self.sonnet_available():
            self.assign_to_sonnet(wo)
        elif self.haiku_available():
            self.assign_to_haiku(wo)
        # ... etc

def is_jules_suitable(self, workorder) -> bool:
    """Check if Jules can handle this workorder."""
    # Parse urgency, complexity, task type
    tags = workorder.get('tags', [])

    # Jules is good at:
    suitable_keywords = ['bug', 'fix', 'refactor', 'test', 'doc', 'feature']

    return any(kw in workorder['content'].lower() for kw in suitable_keywords)

def jules_has_capacity(self) -> bool:
    """Check if Jules has available capacity."""
    # Query Jules API or check local state
    active_sessions = self.get_active_jules_sessions()
    max_concurrent = 3  # Example: allow 3 parallel Jules sessions

    return len(active_sessions) < max_concurrent
```

---

## Implementation Components

### 1. Jules Client Module

**File:** `csc_service/clients/jules/jules.py`

```python
"""Jules client for workorder execution via Jules API."""

from csc_service.shared.log import Log
from csc_service.shared.platform import Platform
import subprocess
import json

class Jules(Log):
    """Jules API client for autonomous coding tasks."""

    def __init__(self):
        super().__init__()
        self.plat = Platform()
        self.api_key = self._load_api_key()
        self.sessions = {}  # Track active sessions

    def _load_api_key(self) -> str:
        """Load Jules API key from config."""
        config_path = self.plat.get_abs_root_path(['config', 'jules_api_key'])
        # Read from file or environment

    def submit_workorder(self, workorder_path: str, repo_url: str) -> str:
        """Submit workorder to Jules, create session, return session ID."""
        # 1. Read workorder content
        with open(workorder_path) as f:
            prompt = f.read()

        # 2. Create Jules session via API/CLI
        session_id = self._create_session(prompt, repo_url)

        # 3. Store session mapping
        self.sessions[session_id] = {
            'workorder': workorder_path,
            'created': time.time(),
            'repo': repo_url,
        }

        self.log(f"Jules session created: {session_id}", "INFO")
        return session_id

    def _create_session(self, prompt: str, repo_url: str) -> str:
        """Create Jules session via CLI or API."""
        # Using CLI (simpler):
        result = subprocess.run([
            'jules', 'remote', 'new',
            '--repo', repo_url,
            '--prompt', prompt,
            '--auto-approve'  # Auto-approve plans (PM made decision)
        ], capture_output=True, text=True)

        # Parse session ID from result
        return self._extract_session_id(result.stdout)

    def check_status(self, session_id: str) -> dict:
        """Check session status."""
        # Via CLI: julius remote list --session session_id
        # Return: {'status': 'running'|'completed'|'failed', 'progress': ...}

    def get_results(self, session_id: str) -> dict:
        """Get completed work (PR link, changes, etc.)."""
        # Via CLI: julius remote pull --session session_id
        # Return: {'pr_url': '...', 'status': 'completed', 'changes': ...}

    def cancel_session(self, session_id: str) -> bool:
        """Cancel active session."""
        # If needed
```

### 2. PM Integration (Enhanced)

**File:** `csc_service/infra/pm.py` (update existing)

```python
def run_cycle(self):
    """Enhanced: Include Jules in assignment logic."""

    ready_wos = self.get_ready_workorders()

    for wo in ready_wos:
        urgency = wo.get('urgency', 'P3')

        if urgency in ['P0', 'P1']:
            # High priority → direct API (sonnet/opus)
            self.assign_to_anthropic(wo)
        elif self._is_jules_task(wo) and self.jules_available():
            # Jules-suitable work + capacity available
            self.assign_to_jules(wo)
        elif urgency == 'P2':
            # Normal priority → queue-worker
            self.assign_to_queue_worker(wo)
        elif urgency == 'P3':
            # Low priority → haiku batch
            self.assign_to_haiku_batch(wo)

    # Monitor Jules sessions
    self._monitor_jules_sessions()

def _is_jules_task(self, workorder) -> bool:
    """Check if workorder is suitable for Jules."""
    content = workorder.get('content', '').lower()
    tags = workorder.get('tags', [])

    jules_keywords = [
        'bug', 'fix', 'refactor', 'test', 'documentation',
        'feature', 'implement', 'debug'
    ]

    return any(kw in content for kw in jules_keywords)

def jules_available(self) -> bool:
    """Check if Jules has capacity."""
    if not self.jules:
        return False

    active = self.get_active_jules_sessions()
    return len(active) < self.max_concurrent_jules  # e.g., 3

def assign_to_jules(self, workorder: dict):
    """Assign workorder to Jules."""
    wo_path = workorder['path']
    repo_url = self.plat.get_abs_root_path(['..', 'repo'])  # Your repo

    try:
        session_id = self.jules.submit_workorder(wo_path, repo_url)

        # Track assignment
        self.store('jules_assignments', {
            **self.load('jules_assignments', {}),
            session_id: {
                'workorder': wo_path,
                'assigned_at': time.time(),
            }
        })

        # Move to wip
        self.move_workorder(wo_path, 'wip')

        self.log(f"Assigned to Jules: {wo_path} (session: {session_id})", "INFO")
    except Exception as e:
        self.log(f"Jules assignment failed: {e}", "ERROR")

def _monitor_jules_sessions(self):
    """Check on active Jules sessions, retrieve results."""
    assignments = self.load('julius_assignments', {})

    for session_id, info in assignments.items():
        status = self.jules.check_status(session_id)

        if status['state'] == 'completed':
            # Get results
            results = self.jules.get_results(session_id)

            # Create PR or integrate results
            pr_url = results.get('pr_url')
            if pr_url:
                self.log(f"Jules completed {info['workorder']}: {pr_url}", "INFO")
                # Move workorder to done
                self.move_workorder(info['workorder'], 'done')
```

### 3. Jules CLI Installation

**File:** Setup/Bootstrap

```bash
# Install Jules CLI globally
npm install -g @google/jules

# Authenticate (opens browser)
jules login

# Verify
jules version
```

### 4. Configuration

**File:** `csc-service.json` (add section)

```json
{
  "services": {},
  "poll_interval": 60,
  "enable_queue_worker": true,
  "enable_test_runner": true,
  "enable_pm": true,
  "enable_pr_review": true,

  "jules": {
    "enabled": true,
    "api_key_path": "config/jules_api_key",
    "max_concurrent_sessions": 3,
    "auto_approve_plans": true,
    "github_repo": "daveylongshaft/csc",
    "github_branch": "main"
  }
}
```

---

## Workflow: From Workorder → Jules → PR

### Step 1: Create Workorder

```bash
workorders add "Fix authentication bug in login.py" : \
  "The login function fails when password contains special chars..."
```

### Step 2: PM Assigns to Jules

```bash
# PM runs every 60s
pm.run_cycle()

# Detects workorder is suitable + Jules has capacity
# Automatically assigns to Jules
```

**Output:**
```
[PM] Analyzing ready workorders...
[PM] WO#1 is Jules-suitable (keywords: fix, bug)
[PM] Jules has capacity (1/3 sessions active)
[PM] Assigning to Jules...
[Jules] Session created: sess-abc123def456
[PM] Moved to wip/
```

### Step 3: Jules Executes

```bash
jules remote list
# sess-abc123def456: RUNNING (plan approved, executing...)

# Jules reads AGENTS.md (if present) for context
# Generates changes to fix the bug
# Creates pull request on GitHub
```

### Step 4: Results Back to CSC

```bash
# PM monitors Jules sessions (every cycle)
[Jules] Session completed: sess-abc123def456
[Jules] Pull request: https://github.com/.../pull/42
[PM] Retrieved results
[PM] Moved WO to done/
[PM] Logged PR link for review
```

### Step 5: Human Review

```bash
# Review Jules's PR on GitHub
# Merge or request changes
# If merged: WO stays in done/
# If rejected: Create fix workorder for Sonnet
```

---

## Files to Create/Modify

### New Files

1. **`csc_service/clients/jules/` (new directory)**
   - `__init__.py`
   - `jules.py` - Jules client class
   - `config.py` - Jules configuration

2. **`tests/test_jules_client.py`**
   - Unit tests for Jules client
   - Mock session creation/status/retrieval

3. **`config/jules_api_key`** (user-provided)
   - Store API key here (git-ignored)

### Modified Files

1. **`csc_service/infra/pm.py`**
   - Add `_is_jules_task()` method
   - Add `assign_to_jules()` method
   - Add `_monitor_julius_sessions()` method
   - Update `run_cycle()` to include Jules logic

2. **`csc-service.json`**
   - Add Jules configuration section

3. **`docs/library/pm.md`** (or create new doc)
   - Document Jules assignment logic
   - Document plan approval workflow
   - Document results handling

4. **`.gitignore`**
   - Add `config/julius_api_key`

---

## Jules Capacity & Throttling

**Questions for your judgment:**

1. **Max concurrent sessions:** How many Jules tasks can run in parallel? (e.g., 3)
2. **Task types:** Which workorder types should PM route to Jules?
3. **Fallback:** If Jules fails, should PM reassign to Sonnet?
4. **Results handling:** Just create PR, or integrate directly into CSC?
5. **GitHub context:** Should Jules see `AGENTS.md` (your codebase documentation)?

---

## Success Criteria

✅ Jules selectable as assignment target (like `workorders assign 1 jules`)
✅ PM auto-decides when to use Jules (capacity + suitability)
✅ Jules sessions created via CLI, plans auto-approved
✅ Status polling: PM monitors active sessions
✅ Results retrieved as PR or integrated code
✅ Workorders move ready → wip → done with Jules tracking
✅ No manual intervention needed (fully automated)
✅ Tests verify Jules client + PM integration
✅ Documentation explains Jules workflow

---

## What Needs Implementation

1. **Jules Client Module** (csc_service/clients/jules/)
   - Session creation via CLI
   - Status checking
   - Results retrieval

2. **PM Enhancement** (csc_service/infra/pm.py)
   - Jules suitability detection
   - Jules capacity checking
   - Jules assignment logic
   - Jules session monitoring

3. **Configuration** (csc-service.json)
   - Jules settings (API key path, concurrency, etc.)

4. **Tests** (tests/test_julius_client.py)
   - Jules client unit tests
   - PM integration tests
   - End-to-end workflow tests

5. **Documentation** (docs/library/)
   - Append Jules section to PM docs
   - Document assignment flow
   - Document plan approval
   - Usage examples

---

**Ready to implement, or do you want to adjust capacity limits, task suitability rules, or result handling first?**
