# PR Review Checklist

## Before You Start

```bash
gh pr diff <number>           # See what changed
gh pr view <number>           # Read the PR description
git log --oneline -10         # Understand recent context
```

Read changed files in **full**, not just the diff. Bugs live in context.

## Invariant Checks

- [ ] **Atomic storage**: Any new JSON writes use temp→fsync→rename pattern? No direct open(file, 'w')?
- [ ] **Disk as truth**: New oper/credential reads go through `@property` (on-demand from disk), not cached?
- [ ] **Lock coverage**: Any shared state accessed from multiple threads? Lock held?
- [ ] **Handler completes write before returning**: Server handlers persist state before returning — still true?

## Cascade Checks

- [ ] **Imports traced**: Find every file that imports the changed module. Do any break?
- [ ] **API compatibility**: Any changed method signatures? All callers updated?
- [ ] **Data format**: Any changed JSON structure? Migration handled? Old data still loads?
- [ ] **IRC protocol**: Any changed message format or numeric? Clients still compatible?

## Agent/Queue Safety

- [ ] **Agent isolation**: queue_worker still spawns agents in temp repos, not CSC_ROOT?
- [ ] **WO lifecycle**: WO still moves correctly: ready→wip→done or back to ready on failure?
- [ ] **Stale detection**: Still tracks WIP growth? Still enforces max runtime?
- [ ] **PM routing**: classify() and prioritize() still correct after changes?

## Test Coverage

- [ ] New behavior has tests?
- [ ] Changed behavior — are existing tests still valid?
- [ ] Edge cases covered (empty input, missing file, network failure)?

## Security (at system boundaries only)

- [ ] Any user-facing input going into shell commands? (command injection)
- [ ] Any file paths constructed from external input? (path traversal)
- [ ] Any new API keys or secrets? (should be in .env, never hardcoded)

## Decision

**APPROVE** when all invariants hold, no cascade breakage, tests adequate.

**REQUEST CHANGES** when: invariant broken, cascading breakage found, storage non-atomic, test coverage missing for changed behavior.

Be specific. "Line 89: `open(path, 'w')` should use atomic write pattern (tmp→fsync→rename), current code risks partial write on crash."
