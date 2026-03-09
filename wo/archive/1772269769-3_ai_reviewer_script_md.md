# Create AI Reviewer Script (bin/ai-reviewer.py)

## Objective
Create `bin/ai-reviewer.py` that analyzes PR diffs and workorder context using Gemini-3-Pro, with fallback to Opus if Gemini is exhausted.

## Script Functionality

### Command-line Interface
```bash
python bin/ai-reviewer.py \
  --workorder commits.txt \
  --diff "git_diff_output" \
  --pr-number 123 \
  [--model opus|gemini-3-pro]
```

### Arguments
- `--workorder` (required): File with commit messages (contains workorder + agent log)
- `--diff` (required): Git diff output showing file changes
- `--pr-number` (required): GitHub PR number
- `--model` (optional): Model choice (default: auto-select Gemini first)

### AI Reviewer Logic

**Step 1: Extract Context**
- Parse workorder content from commit message
- Parse agent execution log from commit message
- Get diff output

**Step 2: Validation Checklist**
Reviewer evaluates:
1. **Scope Compliance**: Do changes match workorder scope?
2. **Infrastructure Protection**: Any unauthorized changes to queue_worker.py, pm.py, etc.?
3. **Security**: Vulnerability check (injection, unsafe subprocess, etc.)
4. **Architecture**: Breaking changes? Threading issues? Cross-platform compatibility?
5. **Quality**: Code conventions? Error handling? Tests?

**Step 3: Model Selection (Intelligent Fallback)**
- **Try Gemini-3-Pro first** (cheaper, good quality)
- **If Gemini fails/quota exceeded**: Fall back to Opus (more expensive, highest quality)
- **If both fail**: Block PR (return exit code 1)

**Step 4: Output Decision**
Generate JSON to `review-result.json`:
```json
{
  "approved": true/false,
  "reason": "explanation of decision",
  "scope_compliant": true/false,
  "infrastructure_safe": true/false,
  "security_safe": true/false,
  "architecture_safe": true/false,
  "quality_acceptable": true/false
}
```

### Environment Variables
- `GOOGLE_API_KEY` - Gemini API credentials
- `ANTHROPIC_API_KEY` - Anthropic API credentials

### Exit Codes
- `0`: Approved (merge is safe)
- `1`: Rejected (review returned APPROVE=false or reviewer unavailable)

## Implementation Notes
- Handle large diffs gracefully (truncate if >5000 lines)
- Log model choice to stderr
- Don't block PR on AI reviewer errors (fallback to Opus)
- If ALL reviewers fail: block PR (safer than auto-approve)
- Timeout protection: max 120 seconds per review

## Testing
- Test with sample PR: protected file change
- Verify Gemini is tried first
- Verify Opus fallback works
- Verify JSON output format
- Verify exit codes (0=approved, 1=rejected)
