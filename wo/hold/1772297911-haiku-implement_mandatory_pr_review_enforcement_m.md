# PR Review Enforcement System

**Objective**: Make PR reviews integral and enforced by script. Infrastructure changes cannot reach production without documented review approval.

## Requirements

### What to Gate
Infrastructure files requiring mandatory review:
- `packages/csc-service/csc_service/infra/pm.py`
- `packages/csc-service/csc_service/infra/queue_worker.py`
- `packages/csc-service/csc_service/main.py`
- `packages/csc-service/csc_service/main.py` (csc-service entry point)
- Any changes to `csc-ctl`, `agent service`, or `test-runner`

### Enforcement Mechanism

1. **Detect Changed Files**
   - git diff --name-only between HEAD~1 and HEAD
   - Check if any gated files modified

2. **Require PR Review Workorder**
   - If gated files changed: create `{agent}-pr_review_COMMIT_{hash}.md` workorder
   - Block further processing until review complete

3. **Review Completion Marker**
   - PR review workorder must end with: `APPROVED` or `APPROVED_WITH_CONDITIONS`
   - If ends with `REJECTED`: move all dependent workorders back to ready/ with error context
   - If ends with `APPROVED_WITH_CONDITIONS`: list required fixes

4. **Gate Production Startup**
   - csc-service should check:
     - Have gated files been modified since last successful review?
     - Is the PM review workorder marked APPROVED?
   - If not: refuse to start, print message about pending review

5. **Integration with PM**
   - PM should skip assigning work if system blocked by pending review
   - Log: "System blocked: pending PR review for infrastructure changes"
   - Don't start test-runner until review complete

### Implementation Details

**PR Review Metadata** (in workorder state)
```
- commit_hash: commit that triggered review
- gated_files: list of modified infrastructure files
- review_status: pending | approved | rejected | approved_with_conditions
- reviewer_notes: feedback from opus/sonnet
- required_fixes: list of issues to resolve before approval
```

**Startup Check** (in main.py before starting services)
```python
if infrastructure_files_changed_without_review():
    print("BLOCKED: Pending PR review for infrastructure changes")
    print("Assign opus-pr_review_* workorder in ready/ to proceed")
    sys.exit(1)
```

**Test-Runner Gate** (before running tests)
```python
if has_gated_file_changes_without_review():
    log("Tests blocked: waiting for infrastructure review approval")
    return  # Skip test cycle
```

## Critical Design Decisions

1. **Who reviews?**
   - opus or sonnet (no other agents)
   - At least one must APPROVE

2. **What blocks production?**
   - Infrastructure files modified → review required
   - Review REJECTED → startup blocked
   - Review PENDING → startup blocked
   - Review APPROVED → startup allowed

3. **Can multiple agents work on same review?**
   - No - PR review is one-per-commit
   - If first reviewer REJECTS, fixes required before new review

4. **Escape hatch?**
   - Emergency production deploy with env var: CSC_SKIP_PR_REVIEW=true
   - Must log warning and email alert (when logging system added)

## Testing

- [ ] Test: Modified pm.py creates PR review workorder
- [ ] Test: Modified queue_worker.py creates PR review workorder
- [ ] Test: Unmodified infrastructure files don't create PR review
- [ ] Test: csc-service refuses to start while PR pending
- [ ] Test: csc-service allows start after PR approved
- [ ] Test: PR REJECTED blocks all related workorders
- [ ] Test: Emergency override works with env var

## Success Criteria

✅ Infrastructure changes automatically create PR review workorders
✅ System refuses to start without approved review
✅ Test-runner blocks tests until review approved
✅ Emergency override available for urgent situations
✅ All infrastructure commits have documented review
