# Create GitHub Actions Workflow for AI Code Review

## Objective
Create `.github/workflows/ai-code-review.yml` that triggers on PR open/update and runs AI code review using Gemini-3-Pro (or Opus fallback).

## Requirements

### Workflow Triggers
- **Event**: Pull request open, synchronize
- **Only on PR branches** (not on main branch pushes)

### Workflow Steps
1. **Checkout code** with full history (fetch-depth: 0)
2. **Extract PR context**:
   - Commit messages (contains workorder content and agent log)
   - Read from `git log origin/main..HEAD --format=%B`
3. **Run AI Reviewer**:
   - Call `python bin/ai-reviewer.py`
   - Pass: workorder context, diff, PR number
   - Environment: ANTHROPIC_API_KEY, GOOGLE_API_KEY
4. **Post review result** to PR:
   - Use GitHub API to post review
   - APPROVE or REQUEST_CHANGES based on ai-reviewer.py output
   - Include detailed review comment

### Environment Variables Needed
- `ANTHROPIC_API_KEY` (secret)
- `GOOGLE_API_KEY` (secret)

### Output
- `review-result.json` file with:
  ```json
  {
    "approved": true/false,
    "comment": "detailed review comment"
  }
  ```

## Implementation Notes
- Use actions/checkout@v4 for getting code
- Use actions/github-script@v7 for posting review
- Fail gracefully if AI reviewer fails (don't auto-approve, block PR)
- Log all steps for debugging
- Handle large diffs (>1MB) gracefully

## Testing
- Create a test PR with protected file change
- Verify GitHub Action runs
- Verify review is posted to PR
- Verify approval/rejection based on changes
