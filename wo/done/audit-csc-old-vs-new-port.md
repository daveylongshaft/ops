<<<<<<< HEAD
You are an AI agent performing a port audit. Work from /opt/csc as your base. Follow every instruction in order. Journal each step by appending to this file before you do it.

## Repos

- OLD: /opt/csc_old  (client-server-commander — original monorepo)
- NEW irc: /opt/csc/irc  (irc.git submodule — all code lives here)
- NEW ops: /opt/csc/ops  (ops.git submodule — WOs, roles, agents)
- WO journal (this file): /opt/csc/ops/wo/wip/audit-csc-old-vs-new-port.md

Move this file to wip/ first:
```
mv /opt/csc/ops/wo/ready/audit-csc-old-vs-new-port.md /opt/csc/ops/wo/wip/audit-csc-old-vs-new-port.md
```

Stamp your PID:
```
echo "PID: $$ starting at $(date)" >> /opt/csc/ops/wo/wip/audit-csc-old-vs-new-port.md
=======
You are an AI agent doing a port audit between an old and new codebase. All your work happens in isolated clones — do not touch anything outside /opt/audit/.

## Your Sandbox

```
/opt/audit/
  irc/        ← irc.git clone  — code to audit and modify
  ops/        ← ops.git clone  — WOs, roles, results (your journal lives here)
  csc_old/    ← client-server-commander.git clone  — read-only reference
```

## Setup — do these first

```bash
# Move this WO to wip
mkdir -p /opt/audit/ops/wo/wip
mv /opt/audit/ops/wo/ready/audit-csc-old-vs-new-port.md \
   /opt/audit/ops/wo/wip/audit-csc-old-vs-new-port.md

# Stamp your PID
echo "PID: $$ starting at $(date)" >> /opt/audit/ops/wo/wip/audit-csc-old-vs-new-port.md

# Create branch in irc for your changes
cd /opt/audit/irc
git checkout -b audit/port-missing-modules
```

Journal every step BEFORE you do it:
```bash
echo "about to <action>" >> /opt/audit/ops/wo/wip/audit-csc-old-vs-new-port.md
>>>>>>> 6ebfb6d4ac421e898daefbb9d7c532df5061d842
```

## Step 1 — Build the audit table

<<<<<<< HEAD
Compare every .py file under /opt/csc_old/packages/csc-service/csc_service/ against its
equivalent in /opt/csc/irc/packages/csc-service/csc_service/.

Also compare:
- /opt/csc_old/tests/test_*.py  vs  /opt/csc/irc/tests/test_*.py
- /opt/csc_old/bin/  vs  /opt/csc/bin/
- /opt/csc_old/deploy/  vs  /opt/csc/irc/deploy/

Write the result to /opt/csc/ops/wo/results/audit-port-table.md in this format:
=======
Compare every .py file in these directory pairs:

| Old | New |
|-----|-----|
| /opt/audit/csc_old/packages/csc-service/csc_service/ | /opt/audit/irc/packages/csc-service/csc_service/ |
| /opt/audit/csc_old/tests/ | /opt/audit/irc/tests/ |
| /opt/audit/csc_old/bin/ | /opt/csc/bin/ |
| /opt/audit/csc_old/deploy/ | /opt/audit/irc/deploy/ |

For each file in old, determine its status in new:
- **PORTED** — equivalent file exists and is functionally equivalent
- **MISSING** — no equivalent found in new
- **PARTIAL** — file exists but incomplete or broken (imports wrong, paths stale, etc.)
- **DROPPED** — intentionally not ported (note why)
- **RENAMED** — ported under a different name

Write result to /opt/audit/ops/wo/results/audit-port-table.md:
>>>>>>> 6ebfb6d4ac421e898daefbb9d7c532df5061d842

```markdown
| File | Old Path | New Path | Status | Notes |
|------|----------|----------|--------|-------|
<<<<<<< HEAD
```

Status: PORTED | MISSING | PARTIAL | DROPPED | RENAMED

Key path mapping rules (old → new):
- imports: `from csc_shared.` → `from csc_service.shared.`
- workorder dirs: `workorders/ready` → `ops/wo/ready`
- root marker: look for `.irc_root` (irc root), `.csc_root` (csc root)
- FTP port: 21 → 9521

## Step 2 — Port MISSING and PARTIAL files

For each MISSING or PARTIAL entry:

1. Read the old file at its old path
2. If it still applies to the new architecture, port it:
   - Update imports to use csc_service.shared.* namespace
   - Update path resolution to walk up to .irc_root marker
   - Update workorder paths to ops/wo/
   - Update any port 21 references to 9521
   - Set file permissions 0664 after writing
3. Write ported file to correct location under /opt/csc/irc/
4. If intentionally dropped, mark DROPPED in table with reason

## Step 3 — Write tests for ported code

For each file ported in Step 2, write or update a test at:
  /opt/csc/irc/tests/test_<module_name>.py

Delete any stale log for that test (rm /opt/csc/irc/tests/logs/test_<module_name>.log) so the test runner picks it up next cycle.

Do NOT run pytest yourself.

## Step 4 — Commit to a branch and create PR

```bash
cd /opt/csc/irc
git checkout -b audit/port-missing-modules
git add .
git commit -m "audit: port missing modules from csc_old"
git push -u origin audit/port-missing-modules
gh pr create \
  --title "audit: port missing modules from csc_old" \
  --body "$(cat <<'EOF'
Ports modules identified as MISSING/PARTIAL in audit.

See ops/wo/results/audit-port-table.md for full comparison table.
See ops/wo/results/audit-port-report.md for summary.
=======
| queue_worker.py | csc_old/.../infra/ | irc/.../infra/ | PORTED | paths updated |
| agent_service.py | csc_old/.../infra/ | — | MISSING | |
```

## Step 2 — Port MISSING and PARTIAL files

For each MISSING or PARTIAL file:

1. Read it from its old path
2. Decide: does it still apply to the new architecture?
3. If yes — port it to the correct path under /opt/audit/irc/, applying:
   - Imports: `from csc_shared.` → `from csc_service.shared.`
   - Root detection: walk up looking for `.irc_root` file (not CLAUDE.md)
   - WO paths: `workorders/ready` → `ops/wo/ready`, `workorders/wip` → `ops/wo/wip`
   - FTP port: `21` → `9521` where it refers to CSC FTP control port
   - Permissions: chmod 0o664 on every file written
4. If no — mark DROPPED with reason in the table

## Step 3 — Write tests

For each file ported in Step 2, write a test at:
```
/opt/audit/irc/tests/test_<module>.py
```

Keep tests focused — import the module, test key functions with mocks where needed.
Delete stale logs if present:
```bash
rm -f /opt/audit/irc/tests/logs/test_<module>.log
```

Do NOT run pytest.

## Step 4 — Commit and create PR

```bash
cd /opt/audit/irc
git add .
git commit -m "audit: port missing modules from csc_old"
git push -u origin audit/port-missing-modules

gh pr create \
  --repo daveylongshaft/irc \
  --title "audit: port missing modules from csc_old" \
  --body "$(cat <<'EOF'
Ports modules identified as MISSING/PARTIAL in csc_old vs csc_new audit.

- Table: ops/wo/results/audit-port-table.md
- Report: ops/wo/results/audit-port-report.md

Tests written for each ported module.
>>>>>>> 6ebfb6d4ac421e898daefbb9d7c532df5061d842
EOF
)"
```

<<<<<<< HEAD
## Step 5 — Write the report

Write /opt/csc/ops/wo/results/audit-port-report.md:

```markdown
# Audit Report: csc_old → csc_new

Date: <date>
Agent: <model name>
PR: <url>

## Summary
- Files checked: X
- PORTED: X
- MISSING (now ported): X
- PARTIAL (now fixed): X
- DROPPED: X (intentional)

## What Remains
<anything not completed in this run>
```

Commit to ops:
```bash
cd /opt/csc/ops
git add wo/results/
git commit -m "audit: port report and table"
git push
```

## Step 6 — Finish

```bash
cd /opt/csc/ops
mv wo/wip/audit-csc-old-vs-new-port.md wo/done/
git add wo/
git commit -m "wo: audit-csc-old-vs-new-port done"
git push
```

Last line of this file when done:
COMPLETE
or
INCOMPLETE: <what remains>
=======
Save the PR URL for the report.

## Step 5 — Write report

Write /opt/audit/ops/wo/results/audit-port-report.md:

```markdown
# Port Audit Report — csc_old → csc_new

Date: <date>
Agent: <model>
PR: <url>

## Counts
- Checked: X
- PORTED: X
- MISSING → now ported: X
- PARTIAL → now fixed: X
- DROPPED: X

## Dropped (intentional)
<list with reasons>

## What Remains
<anything not finished>
```

```bash
cd /opt/audit/ops
git add wo/results/
git commit -m "audit: port table and report"
git push
```

## Step 6 — Close out

```bash
cd /opt/audit/ops
mv wo/wip/audit-csc-old-vs-new-port.md wo/done/
git add wo/
git commit -m "wo: audit-csc-old-vs-new-port complete"
git push
```

Last line — append to the done file before exiting:
```bash
echo "COMPLETE" >> /opt/audit/ops/wo/done/audit-csc-old-vs-new-port.md
# or if something remains:
echo "INCOMPLETE: <what>" >> /opt/audit/ops/wo/done/audit-csc-old-vs-new-port.md
```
PID: 2969648 starting at Mon 09 Mar 2026 05:32:14 PM CDT
about to create branch audit/port-missing-modules in /opt/audit/irc
about to build the audit table
about to port storage.py to /opt/audit/irc/packages/csc-service/csc_service/server/storage.py
about to port collision_resolver.py to /opt/audit/irc/packages/csc-service/csc_service/server/collision_resolver.py
about to port bridge/ to /opt/audit/irc/packages/csc-service/csc_service/bridge/
about to port stats_service/ to /opt/audit/irc/packages/csc-service/csc_service/shared/services/stats_service/
about to port clients/ files from csc_old to /opt/audit/irc/packages/csc-service/csc_service/clients/
about to port cli/ to /opt/audit/irc/packages/csc-service/csc_service/cli/
about to port config.py to /opt/audit/irc/packages/csc-service/csc_service/config.py
about to port server_s2s.py to /opt/audit/irc/packages/csc-service/csc_service/server/server_s2s.py
about to port test_s2s_federation.py to /opt/audit/irc/tests/test_s2s_federation.py
about to commit and push changes
about to commit and push report
about to close out work order
COMPLETE
>>>>>>> 6ebfb6d4ac421e898daefbb9d7c532df5061d842
