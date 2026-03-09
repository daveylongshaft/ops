# Fix csc-service Loop: Add pr-review to Registry + Fix Log Overrides

## Problem

The csc-service daemon loop (main.py lines 66-87) has all 4 service branches but two problems prevent uniform operation:

1. **pr-review not in csc-ctl registry** - SERVICE_KEY_MAP and SERVICE_NAMES don't include pr-review, so `csc-ctl enable/disable/status pr-review` all fail with "Unknown service".

2. **Log() inheritance bug** - Log.log(self, message) accepts 1 arg. TestRunner and PRReviewer call self.log(msg, "ERROR") with 2 args but never override log(). This raises TypeError when error paths execute. QueueWorker already has the correct override.

## Files to Change

### 1. packages/csc-service/csc_service/cli/commands/config_cmd.py (line 13)

Add after "bridge" entry in SERVICE_KEY_MAP:

```python
"pr-review": "enable_pr_review",
```

**Context**: SERVICE_KEY_MAP lines 7-13. Add as new line after line 12.

### 2. packages/csc-service/csc_service/cli/commands/status_cmd.py (line 12)

Add after "enable_bridge" entry in SERVICE_NAMES:

```python
"enable_pr_review": "pr-review",
```

**Context**: SERVICE_NAMES lines 7-13. Add as new line after line 12.

### 3. packages/csc-service/csc_service/infra/test_runner.py (after line 17)

Add log() override method after `self.name = "test-runner"`:

```python
    def log(self, msg, level="INFO"):
        super().log(f"[{level}] {msg}")
```

**Context**: TestRunner.__init__() sets name at line 17. Insert method definition after __init__ or immediately after line 17 (indented to class level).

### 4. packages/csc-service/csc_service/infra/pr_review.py (after line 14)

Add log() override method after `self.name = "pr-review"`:

```python
    def log(self, msg, level="INFO"):
        super().log(f"[{level}] {msg}")
```

**Context**: PRReviewer.__init__() sets name at line 14. Insert method definition after __init__ or immediately after line 14 (indented to class level).

## Verification Steps

After making all 4 changes:

```bash
# Test registry additions
csc-ctl enable pr-review        # Should print "Enabled pr-review" (not "Unknown service")
csc-ctl status                  # Should show pr-review row
csc-ctl disable pr-review       # Should print "Disabled pr-review"

# Test config persistence
cat csc-service.json            # Should have enable_pr_review key

# Test log override (no TypeError on error paths)
csc-ctl cycle test-runner       # Should complete without TypeError
csc-ctl cycle pr-review         # Should complete without TypeError
```

## After Completion

1. Delete test logs to trigger retest:
   ```bash
   rm tests/logs/test_*.log
   ```

2. Commit with descriptive message

3. Push to remote

4. Move this workorder to done/

## Notes

- Architecture is correct - all infra classes inherit Data->Log->Root chain
- Log files go to tempdir/csc/run/{name}.log via Log.log_file property
- Data files go to tempdir/csc/run/{name}_runtime.json via Data.connect()
- This does NOT change main.py (loop already has all 4 branches)
- This does NOT change service_cmd.py cycle (already handles all 4)
START 2026-03-04 16:34:14 PID:31920
Reading code maps to understand structure
Reading config_cmd.py to understand SERVICE_KEY_MAP
Added pr-review to SERVICE_KEY_MAP in config_cmd.py
Reading status_cmd.py to find SERVICE_NAMES
Added enable_pr_review to SERVICE_NAMES in status_cmd.py
Reading test_runner.py to add log() override
Added log() override to TestRunner class
Reading pr_review.py to add log() override
Added log() override to PRReviewer class
Writing tests for pr-review registry and log overrides
Created test_pr_review_registry_and_log.py with 8 test cases
Verifying all code changes are correct
Refreshing code maps with refresh-maps --quick
Verified all changes: registry additions work, log overrides format correctly, test file created
COMPLETE
