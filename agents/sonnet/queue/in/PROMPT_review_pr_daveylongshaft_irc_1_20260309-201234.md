---
role: pr-reviewer
priority: P0
pr: 1
---

# PR Review: #1 — audit: port missing modules from csc_old

**Repository**: daveylongshaft/irc
**Author**: daveylongshaft
**Base**: main ← audit/port-missing-modules

## PR Description

Ports modules identified as MISSING/PARTIAL in csc_old vs csc_new audit.

- Table: ops/wo/results/audit-port-table.md
- Report: ops/wo/results/audit-port-report.md

Tests written for each ported module.

## Changed Files

```
(unavailable)
```

## Diff (first 60KB)

```diff
(diff unavailable)
```

---

## Your Task

Review PR #1 thoroughly using your role checklist.

For each changed file, read the full file from /opt/csc/<path> — the diff is
context only, bugs hide in what surrounds the change.

Answer:
1. Does it do what the title/description claims?
2. Is it progressive (advances the system) or regressive (undoes work, breaks invariants)?
3. Security implications? (injection, path traversal, hardcoded secrets)
4. Does it break anything outside its stated purpose?
5. Storage still atomic where needed?
6. Any import cascades break?
7. Test coverage adequate?

Post your decision:

  # Approve:
  gh pr review 1 --repo daveylongshaft/irc --approve --body "Your findings"

  # Request changes:
  gh pr review 1 --repo daveylongshaft/irc --request-changes --body "Your specific findings"

Then echo COMPLETE.
