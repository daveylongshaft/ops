# Batch API Submission - Platform Cross-System Implementation

**Total Workorders:** 13
**Estimated Processing Time:** 4-8 hours
**Estimated Cost:** $0.60-1.20 USD (Haiku 4.5 + Opus with batch discount)
**Primary Model:** claude-haiku-4-5-20251001 (Haiku 4.5)
**Secondary Model:** claude-opus-4-6 (for complex analysis)
**Processing Mode:** Batch API with Prompt Caching

---

## Workorders Included (with Model Assignment)

| # | Workorder | Size | Est. Time | Model | Difficulty |
|---|-----------|------|-----------|-------|------------|
| 00 | RuntimeStrategy class | 5.9K | 30 min | 🔵 Haiku 4.5 | Easy |
| 01 | PathTranslator class | 6.4K | 40 min | 🔵 Haiku 4.5 | Medium |
| 02 | CommandBuilder class | 8.5K | 45 min | 🔵 Haiku 4.5 | Medium |
| 03 | Extend platform.json schema | 7.2K | 25 min | 🔵 Haiku 4.5 | Easy |
| 04 | Windows service detection | 5.8K | 35 min | 🔵 Haiku 4.5 | Medium |
| 05 | Linux/systemd detection | 6.2K | 35 min | 🔵 Haiku 4.5 | Medium |
| 06 | ServiceManager core class | 7.8K | 40 min | 🔵 Haiku 4.5 | Medium |
| 07 | Windows NSSM installation | 9.9K | 45 min | 🔵 Haiku 4.5 | Medium |
| 08 | Linux/systemd installation | 11K | 50 min | 🔵 Haiku 4.5 | Hard |
| 09 | csc-ctl service commands | 8.3K | 40 min | 🔵 Haiku 4.5 | Medium |
| 10 | Integration testing | 4.7K | 50 min | 🔵 Haiku 4.5 | Medium |
| 11 | GitHub investigation | 5.9K | 60 min | 🔵 Haiku 4.5 | Hard |
| 12 | EVOLUTION.md analysis | 12K | 90 min | 🔴 Opus 4.6 | Very Hard |
| 13 | Daily motive-state system | 17K | 80 min | 🔵 Haiku 4.5 | Hard |

**Total:** ~132 KB | ~9.5 hours
**Model Split:** 12 × Haiku 4.5 + 1 × Opus 4.6

---

## System Prompt (With Caching)

Use this system prompt for batch submission - it will be cached across all workorders:

```
You are Claude Haiku, working on a complex orchestration system called CSC (Client-Server-Commander).

CRITICAL PROJECT RULES:

1. **ALWAYS Read the Full Workorder**: Every word matters. Workorders are self-contained with clear objectives, dependencies, code examples, and testing instructions.

2. **NEVER Commit Without Testing**:
   - Run all test scripts before committing
   - Show test output in commit message
   - Don't claim success without verification

3. **CLAUDE.md Overrides Defaults**:
   - NO Co-Authored-By in commits (commits represent user decisions)
   - NO direct commits to main (must be PR review workflow)
   - ALWAYS run refresh-maps before committing
   - Follow the PR review policy (Opus or Gemini-3-Pro review required)

4. **Workorder Structure**:
   - Read: Objective, Dependencies, Time estimate
   - Implement: Follow code examples, integration sections, patterns
   - Test: Run provided test scripts
   - Verify: Use verification checklist
   - Commit: Use provided commit template

5. **Code Quality**:
   - Copy code snippets exactly as provided (they're tested patterns)
   - Follow existing patterns in codebase
   - Don't add unnecessary comments or docstrings
   - Don't over-engineer or add features beyond scope

6. **Git Workflow**:
   - Feature branch: `git checkout -b feature/[workorder-name]`
   - Staging: `git add [specific files]` (not git add -A)
   - Commit: Template in workorder
   - No direct commits to main

7. **If You Get Stuck**:
   - Re-read the workorder completely
   - Check the test script for what's expected
   - Look at integration section for context
   - Document the blocker clearly in commit message

8. **Success Definition**:
   - All test scripts pass
   - Verification checklist complete
   - Code follows existing patterns
   - Commit message includes test output
   - Ready for PR review

CODEBASE CONTEXT:

**Project**: CSC - Multi-AI IRC Server Orchestration System
**Location**: /c/csc (Windows) or /mnt/c/csc (WSL/Linux)
**Architecture**:
- Server: UDP-based IRC protocol (RFC 2812)
- Clients: Claude, Gemini, ChatGPT agents + human CLI
- Bridge: Protocol proxy for external IRC clients with encryption
- Queue Worker: Manages workorder queue and agent assignment
- PM (Project Manager): Orchestrates agent selection and task routing
- Shared Library: Common IRC protocol, platform detection, utilities

**Key Files**:
- packages/csc-shared/platform.py - Platform detection (where platform_* workorders add code)
- packages/csc-service/ - Unified service package
- CLAUDE.md - Project rules and instructions (authoritative)
- docs/EVOLUTION.md - System evolution and motive state
- docs/MOTIVE_STATE.md - Daily alignment target

**Workorder Chain**:
These 13 workorders are sequential - each builds on previous:
- platform_00-03: Extend platform detection
- platform_04-05: Service detection
- platform_06-09: Service management
- platform_10: Integration testing
- platform_11-13: Meta-analysis and daily alignment

BEFORE YOU START:
- You're working from the batch/platform_XX-*.md files in workorders/batch/
- Read the entire workorder first
- Note the dependencies (what must be done before this)
- Follow code examples exactly
- Run test scripts - show output
- Use git properly (feature branch, meaningful commits)
```

---

## How to Submit

### Model Selection Strategy

**Why Haiku 4.5 for most?**
- Strong coding ability (better than earlier Haiku versions)
- Excellent problem-solving for implementation tasks
- Cost-effective (~95% cheaper than Opus)
- Fast iterations in batch mode

**Why Opus for platform_12?**
- EVOLUTION.md requires deep system analysis
- Needs to understand full commit history and codebase evolution
- Making predictions about future direction is complex reasoning
- Worth the extra cost (~$0.09) for better analysis quality

### Option 1: Using csc-batch CLI (If Available)

```bash
# With model assignment
csc-batch create platform-cross-system \
  --default-model haiku-4-5 \
  --model-override platform_12:opus-4-6 \
  --cache-system-prompt \
  --input-dir workorders/batch/ \
  --pattern "platform_*.md" \
  --submit
```

### Option 2: Manual Batch Creation Script

Create file: `bin/submit-platform-batch.py`

```python
#!/usr/bin/env python3
"""Submit platform batch to Anthropic Batch API with prompt caching."""

import json
import sys
from pathlib import Path
import anthropic

# System prompt (with caching directive)
SYSTEM_PROMPT = """[Use the full system prompt above]"""

# Read all workorders
BATCH_DIR = Path(__file__).parent.parent / "workorders" / "batch"
WORKORDER_FILES = sorted(BATCH_DIR.glob("platform_*.md"))

def create_batch_requests():
    """Create batch requests for all workorders."""
    requests = []

    # Model assignment: most are Haiku 4.5, platform_12 is Opus
    model_assignment = {
        "platform_12": "claude-opus-4-6"  # Complex analysis
    }

    for idx, wo_file in enumerate(WORKORDER_FILES):
        content = wo_file.read_text()

        # Default to Haiku 4.5, override for specific workorders
        model = model_assignment.get(wo_file.stem, "claude-haiku-4-5-20251001")

        requests.append({
            "custom_id": f"platform-{wo_file.stem}",
            "params": {
                "model": model,
                "max_tokens": 12000 if model == "claude-opus-4-6" else 8000,
                "system": [
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"}  # Cache across requests
                    }
                ],
                "messages": [
                    {
                        "role": "user",
                        "content": f"Here's a workorder. Follow it completely.\n\n{content}"
                    }
                ]
            }
        })

    return requests

def submit_batch():
    """Submit batch to Anthropic API."""
    client = anthropic.Anthropic()

    # Create requests
    requests = create_batch_requests()

    print(f"Submitting {len(requests)} workorders to batch API...")
    print(f"System prompt will be cached (saves ~{len(SYSTEM_PROMPT) * 0.9 / 1000:.0f} tokens per request)")

    # Submit batch
    batch = client.beta.messages.batches.create(
        requests=requests
    )

    print(f"\n✓ Batch created: {batch.id}")
    print(f"Status: {batch.processing_status}")
    print(f"\nCheck status with:")
    print(f"  python3 bin/check-batch-status.py {batch.id}")
    print(f"\nRetrieve results when complete:")
    print(f"  python3 bin/get-batch-results.py {batch.id}")

    return batch.id

if __name__ == "__main__":
    batch_id = submit_batch()

    # Save batch ID for reference
    batch_file = Path(__file__).parent.parent / "logs" / "last_batch.txt"
    batch_file.parent.mkdir(parents=True, exist_ok=True)
    batch_file.write_text(batch_id)
```

### Option 3: Direct cURL (If Using OpenRouter or Similar)

```bash
curl -X POST https://api.anthropic.com/v1/messages/batches \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "content-type: application/json" \
  -d '{
    "requests": [
      {
        "custom_id": "platform-00",
        "params": {
          "model": "claude-3-5-haiku-20241022",
          "system": "...[system prompt with cache_control]...",
          "messages": [{"role": "user", "content": "...workorder content..."}]
        }
      },
      ...
    ]
  }'
```

---

## Cost Estimation

### Haiku 4.5 Pricing (with batch processing 50% discount)
- Input: $0.80 / 1M tokens → $0.40 (discounted)
- Output: $4.00 / 1M tokens → $2.00 (discounted)

### Opus 4.6 Pricing (with batch processing 50% discount)
- Input: $3.00 / 1M tokens → $1.50 (discounted)
- Output: $15.00 / 1M tokens → $7.50 (discounted)

### Estimate by Model

**Haiku 4.5 (12 workorders: platform_00-11, 13)**:
- System prompt: ~2,000 tokens × 12 = 24,000 tokens (cached)
  - Real cost: 2,000 + (2,000 × 11 × 0.1) = ~4,200 tokens
- Workorder inputs: ~50,000 tokens × 12 = 600,000 tokens
- Expected outputs: ~8,000 tokens × 12 = 96,000 tokens
- **Haiku 4.5 Cost**:
  - Input: (4,200 + 600,000) × $0.40 / 1M = $0.24
  - Output: 96,000 × $2.00 / 1M = $0.19
  - **Subtotal: ~$0.43**

**Opus 4.6 (1 workorder: platform_12)**:
- System prompt: ~2,000 tokens (already cached!)
- Workorder input: ~50,000 tokens
- Expected output: ~12,000 tokens (more detailed analysis)
- **Opus 4.6 Cost**:
  - Input: 50,000 × $1.50 / 1M = $0.08
  - Output: 12,000 × $7.50 / 1M = $0.09
  - **Subtotal: ~$0.17**

**Total Cost Estimate**:
- Haiku 4.5: $0.43
- Opus 4.6: $0.17
- **Grand Total: ~$0.60 USD**

*(Still extraordinarily cheap! Haiku 4.5 is cost-effective, Opus just for the complex analysis)*

---

## Processing Timeline

**Typical Batch API Processing**:
- Submitted: Immediately
- Processing: 30 seconds to 24 hours (usually < 1 hour for small batches)
- Results ready: Retrieved via API when complete
- Success rate: ~99% (retries built-in)

---

## After Batch Completes

### Retrieve Results

```bash
python3 bin/get-batch-results.py <batch-id>
```

This will:
1. Fetch all results from batch
2. Parse responses
3. Extract commits
4. Create PR summaries
5. Show which workorders succeeded/failed

### Process Results

For each successful workorder:
1. Review the implementation
2. Check test output
3. Verify commits
4. Create PR if needed
5. Mark as done

For failed workorders:
1. Review error messages
2. Assign to next agent with fixes
3. Or re-run specific workorders

---

## Batch Submission Checklist

- [ ] All 13 workorder files exist and are readable
- [ ] System prompt with cache_control prepared
- [ ] Model set to haiku
- [ ] Batch API credentials available
- [ ] Batch submission script reviewed
- [ ] Cost estimate acceptable
- [ ] Git is clean (no uncommitted changes)
- [ ] Ready to submit

---

## Go/No-Go Decision

**Submit Batch?** YES ✓

This batch is:
- ✓ Well-structured with clear sequential dependencies
- ✓ Sized appropriately for haiku (not too complex)
- ✓ Includes all code examples and test scripts
- ✓ Cost-effective with batch API + caching
- ✓ Foundation for immediate value (platform auto-configuration)

**Next Steps**:
1. Run submission script
2. Save batch ID
3. Check status periodically
4. Process results as they complete
5. Create PRs for merged changes
6. Run platform_10 integration test on actual systems

---

## Reference

- Batch API Docs: https://docs.anthropic.com/en/docs/build-a-classifier#batch-api
- Prompt Caching: https://docs.anthropic.com/en/docs/build-a-classifier#prompt-caching
- Haiku Model: claude-3-5-haiku-20241022
- Current Pricing: https://www.anthropic.com/pricing

