# Create PR Creator Helper Module (packages/csc-service/csc_service/infra/pr_creator.py)

## Objective
Create `pr_creator.py` module that provides functions to create GitHub PRs via the GitHub API when queue_worker detects protected file changes.

## Module Functions

### `create_pr(github_token, owner, repo, title, body, head, base="main")`
Creates a pull request via GitHub REST API.

**Parameters:**
- `github_token` (str): GitHub API token with repo access
- `owner` (str): Repository owner (username or org)
- `repo` (str): Repository name
- `title` (str): PR title (< 70 chars)
- `body` (str): PR description (includes workorder, agent log, instructions)
- `head` (str): Feature branch name (e.g., "feature/agent-haiku-wo-123")
- `base` (str): Target branch (default: "main")

**Returns:**
- `dict`: PR response with `number`, `html_url`, `state`
- `None`: If creation fails

**Behavior:**
- Use GitHub REST API v3 (`/repos/{owner}/{repo}/pulls`)
- Set headers: `Authorization: token <token>`, `Content-Type: application/json`
- Handle errors: connection, auth, rate limiting
- Log success: PR URL, number
- Log failure: error message, status code

### `get_changed_files(repo_path, base_sha, head_sha)`
Get list of files changed between two commits.

**Parameters:**
- `repo_path` (str): Path to git repo
- `base_sha` (str): Base commit SHA (e.g., "origin/main")
- `head_sha` (str): Head commit SHA (e.g., "HEAD")

**Returns:**
- `list[str]`: File paths that changed

**Behavior:**
- Use `git diff --name-only base..head`
- Return empty list if comparison fails

### `is_protected_file(filepath)`
Check if a file path is in a protected path.

**Parameters:**
- `filepath` (str): File path (e.g., "packages/csc-service/queue_worker.py")

**Returns:**
- `bool`: True if file is protected, False otherwise

**Protected Paths:**
- `packages/**/*.py`
- `bin/**` (all scripts)
- `*.json` (all config files)
- `*.yaml`, `*.yml` (all YAML config)
- All other files (default: protected)

**Unprotected Paths:**
- `agents/**` (queue management)
- `workorders/**` (workorder lifecycle)
- `staging_uploads/**` (service uploads)
- `services/**` (dynamic services)

### `prepare_pr_body(workorder_content, agent_log, commit_diff)`
Format the PR description with full context.

**Parameters:**
- `workorder_content` (str): What was requested
- `agent_log` (str): Agent execution log
- `commit_diff` (str): Git diff output

**Returns:**
- `str`: Formatted markdown for PR description

**Format:**
```markdown
## Workorder
{workorder}

## Agent Execution Log
{agent_log}

## Changes
{diff_preview}

## Review Checklist
- [ ] Changes match workorder scope
- [ ] No unauthorized infrastructure changes
- [ ] Security safe (no injection, proper subprocess)
- [ ] Architecture sound (no breaking changes)
- [ ] Code quality acceptable

_This PR was created by Queue Worker due to protected file changes._
_Awaiting AI code review (Gemini-3-Pro/Opus)._
```

## Configuration

Module should read from `csc-service.json`:
```json
{
  "queue-worker": {
    "github_token": "ghp_...",
    "github_repo": "owner/repo"
  }
}
```

## Error Handling
- Catch connection errors (network unavailable)
- Catch auth errors (invalid token)
- Catch rate limiting (429 status)
- Log all errors clearly
- Never silent-fail (always report to caller)

## Testing
- Test with real GitHub token
- Create test PR to test repo
- Verify PR appears on GitHub
- Verify PR has correct title/body
- Test with invalid token (error handling)
- Test with network error (error handling)
