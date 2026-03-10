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
```

## Step 1 — Build the audit table

Compare every .py file under /opt/csc_old/packages/csc-service/csc_service/ against its
equivalent in /opt/csc/irc/packages/csc-service/csc_service/.

Also compare:
- /opt/csc_old/tests/test_*.py  vs  /opt/csc/irc/tests/test_*.py
- /opt/csc_old/bin/  vs  /opt/csc/bin/
- /opt/csc_old/deploy/  vs  /opt/csc/irc/deploy/

Write the result to /opt/csc/ops/wo/results/audit-port-table.md in this format:

```markdown
| File | Old Path | New Path | Status | Notes |
|------|----------|----------|--------|-------|
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
EOF
)"
```

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
