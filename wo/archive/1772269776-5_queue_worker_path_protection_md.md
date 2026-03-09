# Modify Queue Worker for Path-Based Protection

## Objective
Add path-based git protection logic to `queue_worker.py` so that:
- **Unprotected paths** (agents/, workorders/, services/) → Direct push to main (no delay)
- **Protected paths** (packages/, bin/, *.json) → Feature branch + PR + AI review

## Current Code Flow
The function `git_commit_push_in_repo()` at line 194 currently:
1. Stages all changes with `git add -A`
2. Commits with message
3. Pushes to main

## Required Modifications

### 1. Add Path Protection Check (New Function)
Create a new function in queue_worker.py:

```python
def get_protected_files(repo_path, base_sha="origin/main", head_sha="HEAD"):
    """Get list of protected files changed in this commit."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_sha}...{head_sha}"],
            cwd=str(repo_path),
            capture_output=True, text=True, timeout=30
        )
        changed_files = result.stdout.strip().split('\n') if result.stdout else []

        PROTECTED_PATTERNS = [
            "packages/", "bin/", "*.json", "*.yaml", "*.yml"
        ]
        UNPROTECTED_PATTERNS = [
            "agents/", "workorders/", "staging_uploads/", "services/"
        ]

        protected = []
        for f in changed_files:
            # Check if file matches unprotected pattern first
            if any(f.startswith(pattern) for pattern in UNPROTECTED_PATTERNS):
                continue
            # Check if matches protected pattern
            if any(f.startswith(pattern) or f.endswith(pattern)
                   for pattern in PROTECTED_PATTERNS):
                protected.append(f)
            else:
                # Default: protected (safe default)
                protected.append(f)

        return protected
    except Exception as e:
        log(f"Failed to check protected files: {e}", "WARN")
        return []  # Assume unprotected on error (allow push)
```

### 2. Modify git_commit_push_in_repo() Function
Update the function at line 194 to:

```python
def git_commit_push_in_repo(repo_path, message, label="",
                            workorder_content="", agent_log=""):
    """Stage all, commit, push - with path-based protection.

    Protected files → feature branch + PR creation
    Unprotected files → direct push to main
    """
    desc = f" ({label})" if label else ""

    # Stage changes
    try:
        subprocess.run(["git", "add", "-A"], cwd=str(repo_path),
                      capture_output=True, timeout=30)
    except Exception as e:
        log(f"git add failed in {repo_path}: {e}", "ERROR")
        return

    # Check for changes
    result = subprocess.run(["git", "status", "--porcelain"], cwd=str(repo_path),
                           capture_output=True, text=True)
    if not result.stdout.strip():
        log(f"Nothing to commit in {repo_path}{desc}")
        return

    # Commit
    log(f"git commit in {repo_path}{desc}: {message.splitlines()[0][:80]}")
    try:
        subprocess.run(["git", "commit", "-m", message], cwd=str(repo_path),
                      capture_output=True, timeout=30)
    except Exception as e:
        log(f"git commit failed in {repo_path}: {e}", "ERROR")
        return

    # **NEW**: Check for protected files
    protected_files = get_protected_files(repo_path)

    if protected_files:
        # PROTECTED: Create feature branch + PR
        log(f"Protected files detected: {protected_files}")
        log(f"Creating feature branch + PR instead of direct push")

        # Create feature branch name
        agent_name = os.environ.get("CSC_AGENT_NAME", "unknown")
        ts = int(time.time())
        feature_branch = f"feature/agent-{agent_name}-{ts}"

        try:
            # Checkout feature branch
            subprocess.run(
                ["git", "checkout", "-b", feature_branch],
                cwd=str(repo_path),
                capture_output=True, timeout=30
            )

            # Push feature branch
            subprocess.run(
                ["git", "push", "-u", "origin", feature_branch],
                cwd=str(repo_path),
                capture_output=True, timeout=60
            )

            # Create PR via GitHub API
            try:
                from csc_service.infra.pr_creator import create_pr

                # Read config
                config = load_config()
                github_token = config.get("github_token")
                github_repo = config.get("github_repo", "owner/repo")

                if github_token:
                    owner, repo = github_repo.split("/")
                    pr_title = f"Agent {agent_name}: {message.splitlines()[0][:50]}"
                    pr_body = prepare_pr_description(
                        workorder_content, agent_log, protected_files
                    )

                    pr = create_pr(
                        github_token, owner, repo,
                        pr_title, pr_body,
                        head=feature_branch, base="main"
                    )

                    if pr:
                        log(f"Created PR: {pr['html_url']}")
                    else:
                        log(f"Failed to create PR", "ERROR")
            except Exception as e:
                log(f"PR creation failed: {e}", "WARN")

        except Exception as e:
            log(f"Feature branch creation failed: {e}", "ERROR")
            return

    else:
        # UNPROTECTED: Direct push to main
        log(f"Only unprotected files modified, pushing directly to main")

        git_pull_in_repo(repo_path, desc)

        log(f"git push from {repo_path}{desc}")
        try:
            result = subprocess.run(["git", "push"],
                            cwd=str(repo_path),
                            capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                log(f"git push failed from {repo_path}: {result.stderr}", "WARN")
        except Exception as e:
            log(f"git push failed from {repo_path}: {e}", "WARN")
```

### 3. Add Helper Functions
Add these new helper functions to queue_worker.py:

```python
def load_config():
    """Load csc-service.json config."""
    config_file = CSC_ROOT / "csc-service.json"
    if config_file.exists():
        try:
            return json.loads(config_file.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {}

def prepare_pr_description(workorder_content, agent_log, protected_files):
    """Format PR body with context."""
    return f"""## Workorder
{workorder_content}

## Protected Files Changed
{json.dumps(protected_files, indent=2)}

## Agent Execution Log
{agent_log}

## Review Required
This PR modifies protected infrastructure code and requires AI review before merge.

Awaiting Gemini-3-Pro (or Opus) review via GitHub Actions.
"""
```

## Call Sites to Update

1. **Line 821**: In `process_work()`, when committing agent temp repo:
   ```python
   git_commit_push_in_repo(
       agent_repo,
       commit_msg_agent,
       label=f"agent {agent_name} temp repo",
       workorder_content=...,  # Extract from WIP
       agent_log=...  # Read from agent log
   )
   ```

2. **Line 986**: When committing main repo after agent finishes:
   ```python
   git_commit_push(commit_msg)  # Use existing function (no changes needed for main repo)
   ```

## Testing Requirements
- Test unprotected change (agents/ only) → Direct push
- Test protected change (packages/queue_worker.py) → Feature branch + PR
- Test mixed change (both types) → Feature branch + PR (safe default)
- Verify feature branch is created
- Verify PR is created with correct body
- Verify git push succeeds for both cases
