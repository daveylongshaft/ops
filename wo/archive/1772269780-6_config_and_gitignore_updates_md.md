# Update Configuration and .gitignore

## Objective
Update `csc-service.json` with GitHub API credentials and PR creation config, and update `.gitignore` to exclude AI reviewer output files.

## csc-service.json Updates

### Current Structure
Read the current `csc-service.json` and add a new `"path-protection"` section:

```json
{
  "path-protection": {
    "enabled": true,
    "github_token": "${GITHUB_TOKEN}",
    "github_repo": "owner/repo",
    "protected_paths": [
      "packages/**/*.py",
      "bin/**",
      "*.json",
      "*.yaml",
      "*.yml"
    ],
    "unprotected_paths": [
      "agents/**",
      "workorders/**",
      "staging_uploads/**",
      "services/**"
    ]
  }
}
```

### Configuration Details

- **`enabled`**: Boolean to toggle protection (default: true)
- **`github_token`**: GitHub API token (read from env var `GITHUB_TOKEN`)
  - Should be a Personal Access Token with `repo` scope
  - Can also be read from `.env` file
- **`github_repo`**: Repository in format "owner/repo"
  - Example: "anthropics/csc"
- **`protected_paths`**: List of glob patterns for protected files
  - All matching files require PR + review
- **`unprotected_paths`**: List of glob patterns for unprotected files
  - Can push directly to main without review

### Environment Variable Fallback
If `github_token` is not in csc-service.json, fall back to:
1. `GITHUB_TOKEN` environment variable
2. `.env` file `GITHUB_TOKEN=...` line

## .gitignore Updates

Add the following lines to `.gitignore` to exclude AI reviewer temporary files:

```
# AI Reviewer temporary files (GitHub Actions)
review-result.json
commits.txt

# Potential credentials/tokens (should never commit)
.env.local
.env.*.local
```

### Rationale
- `review-result.json` - Temporary output from `bin/ai-reviewer.py` (not needed in git)
- `commits.txt` - Temporary file used to extract commit messages (workflow artifact)
- `.env.*` - Local environment variable files (never commit secrets)

## Verification Steps

### csc-service.json
1. Read current csc-service.json
2. Verify it's valid JSON
3. Add `path-protection` section if not present
4. Keep all existing sections intact
5. Verify updated JSON is still valid

### .gitignore
1. Read current .gitignore
2. Append new lines (avoid duplicates)
3. Verify file is still readable/valid

### Testing
1. Verify `csc-ctl show` can read the config
2. Verify `csc-ctl config path-protection` shows new section
3. Create a test file named `review-result.json` - should be ignored by git
4. Verify `git status` doesn't show the test file
