# Testing and Validation

## Objective
Verify that the path-based git protection system works correctly:
- Protected paths trigger PR creation + AI review
- Unprotected paths push directly to main (no delay)
- AI reviewer approves/rejects based on validation criteria

## Test Setup

### Prerequisites
1. All 6 previous workorders MUST be complete:
   - GitHub Actions workflow created
   - CODEOWNERS file created
   - AI reviewer script deployed
   - PR creator module implemented
   - Queue worker modified
   - Config and .gitignore updated
2. GitHub token configured in csc-service.json
3. GitHub Actions enabled for the repository

## Test 1: Unprotected Path (Direct Push)

### Setup
```bash
git checkout -b test-unprotected
echo "test content" > agents/haiku/queue/in/test-orders.md
git add agents/
git commit -m "test: unprotected path change"
```

### Expected Behavior
- Commit goes directly to main
- No PR created
- No GitHub Actions workflow triggered
- Changes immediately visible in main branch

### Verification
```bash
git log main | grep "test: unprotected path change"  # Should find it
git branch -D test-unprotected
```

## Test 2: Protected Path (PR + Review)

### Setup
```bash
git checkout -b test-protected
echo "# test" >> packages/csc-service/csc_service/infra/pm.py
git add packages/
git commit -m "test: protected path change"
git push origin test-protected
```

### Expected Behavior
1. Push to feature branch succeeds
2. PR is created automatically (by queue_worker or manually)
3. GitHub Actions workflow triggers
4. AI reviewer analyzes the PR
5. Review is posted to PR (APPROVE or REQUEST_CHANGES)
6. Cannot merge until review is approved

### Verification via GitHub
```
1. Visit GitHub repo → Pull Requests
2. Find the test PR
3. Check if GitHub Actions workflow is running
4. Wait for review comment to appear
5. Verify review verdict (✓ approved or ✗ requested changes)
```

### Verification via CLI
```bash
gh pr list --search "test-protected"
gh pr view <PR_NUMBER> --web  # Open PR in browser
gh pr checks <PR_NUMBER>      # Check workflow status
```

## Test 3: Mixed Changes (Protected + Unprotected)

### Setup
```bash
git checkout -b test-mixed
echo "# agent work" > agents/haiku/queue/in/mixed.md
echo "# code change" >> packages/csc-service/csc_service/infra/queue_worker.py
git add .
git commit -m "test: mixed protected and unprotected changes"
git push origin test-mixed
```

### Expected Behavior
- Protected files trigger feature branch + PR (safe default)
- Unprotected files are also included in the PR
- PR shows all changes
- AI reviewer sees both protected and unprotected files

### Verification
```bash
gh pr view <PR_NUMBER> --web
# Verify PR contains both changes
# Verify AI review is requested for protected files
```

## Test 4: AI Reviewer Approval

### Setup
Create a PR with a legitimate infrastructure change that matches workorder:

```bash
git checkout -b test-legitimate-change
# Make a small, safe change that clearly improves code quality
# Example: add docstring, fix import order, etc.
git commit -m "docs: improve docstring in queue_worker.py"
git push origin test-legitimate-change
```

### Expected Behavior
1. PR is created
2. GitHub Actions runs AI reviewer
3. AI reviewer analyzes:
   - Scope: Change matches description (docstring improvement)
   - Infrastructure: No unauthorized changes
   - Security: Safe (just documentation)
   - Architecture: No impact
   - Quality: Improves code
4. Result: **APPROVED** ✓
5. Can merge to main

### Verification
```bash
# Check PR status - should show "Approved"
gh pr view <PR_NUMBER>
# Should show review: APPROVED by ai-reviewer bot
```

## Test 5: AI Reviewer Rejection

### Setup
Create a PR with suspicious changes:

```bash
git checkout -b test-malicious-change
# Make a change that looks dangerous/unauthorized
# Example: add subprocess.call() without validation
echo "subprocess.call(some_user_input)" >> packages/csc-service/csc_service/infra/pm.py
git commit -m "add: subprocess execution"
git push origin test-malicious-change
```

### Expected Behavior
1. PR is created
2. GitHub Actions runs AI reviewer
3. AI reviewer detects:
   - Scope: Not mentioned in workorder
   - Security: Potential injection vulnerability
   - Result: **REJECTED** ✗
4. PR shows "Approval required"
5. Cannot merge without manual approval

### Verification
```bash
# Check PR status - should show "Changes Requested"
gh pr view <PR_NUMBER>
# Should show review: REQUEST_CHANGES from ai-reviewer
# Review comment should explain why it was rejected
```

## Test 6: GitHub Actions Workflow

### Verify Workflow Runs
1. Go to GitHub → Actions tab
2. Find workflow: "AI Code Review"
3. Check that it runs on PR open/update
4. Verify it doesn't run on direct pushes to main

### Workflow Steps to Verify
- [ ] Checkout code
- [ ] Extract commit messages
- [ ] Run AI reviewer
- [ ] Post review to PR
- [ ] Update status checks

## Cleanup

After testing, clean up test branches:
```bash
# Delete local test branches
git branch -D test-unprotected test-protected test-mixed test-legitimate-change test-malicious-change

# Delete remote test branches
git push origin --delete test-unprotected test-protected test-mixed test-legitimate-change test-malicious-change

# Close test PRs on GitHub (if any still open)
gh pr close <PR_NUMBER> --delete-branch
```

## Success Criteria

All tests must pass:
- [x] Unprotected paths push directly (no PR)
- [x] Protected paths create PRs
- [x] GitHub Actions workflow runs
- [x] AI reviewer approves legitimate changes
- [x] AI reviewer rejects suspicious changes
- [x] PR status updates correctly
- [x] Branch protection works (can't merge without approval)
- [x] Cleanup successful (no stray branches/PRs)

## Known Issues / Troubleshooting

**GitHub Actions not running:**
- Check: Actions tab enabled in repo settings
- Check: Workflow file syntax in `.github/workflows/ai-code-review.yml`
- Check: Secrets (ANTHROPIC_API_KEY, GOOGLE_API_KEY) configured

**AI reviewer not posting comment:**
- Check: GitHub token has `repo` scope
- Check: Review script returns valid JSON
- Check: GitHub API token is not expired

**PR creation fails:**
- Check: `github_token` configured in csc-service.json
- Check: Token has `repo` access
- Check: Repository format correct ("owner/repo")

**Path detection incorrect:**
- Check: Protected path patterns match files
- Check: Git diff output is correct
- Verify: `get_protected_files()` logic in queue_worker.py
