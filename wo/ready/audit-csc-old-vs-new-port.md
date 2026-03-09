---
role: pm-worker
priority: P1
agent: gemini-2.5-pro-preview
---

# Audit: csc_old vs csc_new — What Was Not Ported

## Environment

```
C:\fahu\audit\
  csc_new\          ← csc.git (umbrella)
    irc\            ← irc.git submodule  (code lives here)
    ops\            ← ops.git submodule  (WOs, roles, agents live here)
  csc_old\          ← client-server-commander.git (original monorepo)
```

Run `ops\bin\setup-audit-fahu.ps1` first if repos are not yet cloned.

Your working directory when doing code changes: `C:\fahu\audit\csc_new\irc`
Your WO journal (this file): `C:\fahu\audit\csc_new\ops\wo\wip\audit-csc-old-vs-new-port.md`

## Scope

Compare `csc_old\` against `csc_new\irc\` and `csc_new\ops\` to determine:

1. What was fully ported
2. What was partially ported or broken in the port
3. What was intentionally dropped (note why)
4. What is missing and should be ported

Focus areas (in priority order):

| Area | Old Path | New Path |
|------|----------|----------|
| Infra loop | `packages/csc-service/csc_service/infra/` | `irc/packages/csc-service/csc_service/infra/` |
| Tests | `tests/` | `irc/tests/` |
| Shared lib | `packages/csc-shared/` | `irc/packages/csc-service/csc_service/shared/` |
| Server | `packages/csc-server/` | `irc/packages/csc-service/csc_service/server/` |
| Clients | `packages/csc-claude/`, `csc-gemini/`, etc | `irc/packages/csc-service/csc_service/clients/` |
| Bridge | `packages/csc-bridge/` | `irc/packages/csc-service/csc_service/` |
| Bin scripts | `bin/` | `bin/` (csc root) |
| Deploy | `deploy/` | `irc/deploy/` |
| Docs | `docs/` | `irc/` root docs + ops docs |
| Config | `etc/`, `csc-service.json` | `irc/` root |
| Tests support | `tests/conftest.py`, `platform_gate.py` | `irc/tests/` |

## Your Process

### Step 1 — Build the audit table

Walk every `.py` file in `csc_old\packages\csc-service\csc_service\` and check
if an equivalent exists in `csc_new\irc\packages\csc-service\csc_service\`.

Produce a table in `ops\wo\results\audit-port-table.md`:

```markdown
| File | Old Path | New Path | Status | Notes |
|------|----------|----------|--------|-------|
| test_runner.py | packages/.../infra/ | irc/.../infra/ | PORTED | path logic updated |
| agent_service.py | packages/.../infra/ | irc/.../infra/ | MISSING | not found in irc |
| ... | | | | |
```

Status values: `PORTED` | `MISSING` | `PARTIAL` | `DROPPED` | `RENAMED`

Also check:
- `csc_old\tests\test_*.py` vs `csc_new\irc\tests\test_*.py`
- `csc_old\bin\` vs `csc_new\bin\`
- `csc_old\deploy\` vs `csc_new\irc\deploy\`

### Step 2 — Port what is MISSING or PARTIAL

For each MISSING/PARTIAL file:

1. Read the old file
2. Determine if it still applies to the new architecture
3. If yes: port it to the correct location in `csc_new\irc\`, updating:
   - Import paths (`csc_service.shared.*` not `csc_shared.*`)
   - Path resolution to use `.irc_root` marker
   - Workorder paths from `workorders/` to `ops/wo/`
   - Port numbers: FTP control = 9521, CSC = 9525
4. If dropped intentionally: note reason in table with `DROPPED`

### Step 3 — Write tests for ported code

For each file ported in Step 2, write or update a test in `irc\tests\test_<module>.py`.
Delete the log if it exists so test runner picks it up next cycle.

Do NOT run tests yourself.

### Step 4 — Commit to a branch and create PR

```bash
cd C:\fahu\audit\csc_new\irc
git checkout -b audit/port-missing-modules
git add .
git commit -m "audit: port missing modules from csc_old"
git push -u origin audit/port-missing-modules
gh pr create --title "audit: port missing modules from csc_old" \
  --body "Ports modules identified as MISSING/PARTIAL in audit-port-table.md"
```

### Step 5 — Write report

Write `C:\fahu\audit\csc_new\ops\wo\results\audit-port-report.md`:

```markdown
# Audit Report: csc_old → csc_new Port

Date: <date>
Agent: <your name>

## Summary
- X files checked
- X PORTED
- X MISSING (now ported in this PR)
- X PARTIAL (fixed in this PR)
- X DROPPED (see table for reasons)

## PR
<link>

## What Remains
<anything not completed>
```

Commit and push to ops.git:
```bash
cd C:\fahu\audit\csc_new\ops
git add wo/results/
git commit -m "audit: port report"
git push
```

### Step 6 — Move WO

```bash
mv ops\wo\wip\audit-csc-old-vs-new-port.md ops\wo\done\
cd C:\fahu\audit\csc_new\ops
git add wo/
git commit -m "wo: audit-csc-old-vs-new-port done"
git push
```

## Rules

- Journal every step to this WO file with `echo` BEFORE doing it
- Do NOT run tests — delete the log, let the runner pick it up
- Do NOT commit directly to main on irc.git — use the `audit/port-missing-modules` branch
- Permissions: new files 0664, dirs 0775
- No AI attribution in commits
- Last line of this WO when done: `COMPLETE` or `INCOMPLETE: <what remains>`
