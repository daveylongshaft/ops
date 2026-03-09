# Parallel Batch Execution Guide

**Script**: `bin/submit-platform-batch-parallel.py`
**Mode**: Dependency-aware parallel submission
**Models**: Haiku 4.5 (primary) + Opus 4.6 (complex analysis)
**Cost**: ~$0.60 USD
**Time**: 4-8 hours total

---

## How It Works

The script analyzes dependencies and submits workorders in **waves**, where each wave contains workorders that can run in parallel:

```
Wave 1: [platform_00]                          (platform.py foundation)
Wave 2: [platform_01]                          (depends on wave 1)
Wave 3: [platform_02]                          (depends on wave 1-2)
Wave 4: [platform_03]                          (depends on wave 1-3)
Wave 5: [platform_04, platform_05]             (parallel - both depend on 1-4)
Wave 6: [platform_06]                          (depends on 5)
Wave 7: [platform_07, platform_08]             (parallel - both depend on 6)
Wave 8: [platform_09]                          (depends on 7)
Wave 9: [platform_10]                          (depends on 8)
Wave 10: [platform_11]                         (depends on 9)
Wave 11: [platform_12]                         (Opus - depends on 10)
Wave 12: [platform_13]                         (depends on 11)
```

**Parallel Opportunity**: Waves 5 and 7 run multiple workorders simultaneously via Anthropic Batch API.

---

## To Run

### Quick Start

```bash
python3 bin/submit-platform-batch-parallel.py
```

### What Happens

1. **Dependency Analysis** - Determines which workorders can run in parallel
2. **Wave 1 Submission** - Sends platform_00 to API
3. **Wave 1 Wait** - Waits for completion
4. **Wave 2 Submission** - Sends platform_01
5. ... continues through all 12 waves
6. **Results** - Displays summary of all completed workorders

### Output Example

```
============================================================
PLATFORM BATCH SUBMISSION - PARALLEL WITH DEPENDENCIES
============================================================

Dependency analysis:
Total workorders: 13
Batch waves: 12

Batch structure:
  Wave 1: [platform_00]
  Wave 2: [platform_01]
  Wave 3: [platform_02]
  Wave 4: [platform_03]
  Wave 5: [platform_04, platform_05]
  ...

============================================================
WAVE 1/12: Preparing batch
============================================================
Loading platform_00... ✓ (Haiku 4.5)
Submitting to Anthropic Batch API... ✓
Batch ID: msr_batch_0123456789abcdef
Status: processing

Waiting for batch 1/12 to complete...... ✓ DONE

Results: 1 succeeded, 0 errored

Results summary for wave 1:
  ✓ SUCCESS: platform-platform_00
```

---

## Expected Timeline

| Wave | Workorders | Processing | Total Time |
|------|-----------|-----------|-----------|
| 1 | 1 | ~30 min | ~30 min |
| 2 | 1 | ~40 min | ~70 min |
| 3 | 1 | ~45 min | ~115 min |
| 4 | 1 | ~25 min | ~140 min |
| **5** | **2 (parallel)** | **~40 min** | **~180 min** |
| 6 | 1 | ~40 min | ~220 min |
| **7** | **2 (parallel)** | **~50 min** | **~270 min** |
| 8 | 1 | ~40 min | ~310 min |
| 9 | 1 | ~50 min | ~360 min |
| 10 | 1 | ~60 min | ~420 min |
| 11 | 1 (Opus) | ~90 min | ~510 min |
| 12 | 1 | ~80 min | ~590 min |

**Total: ~9.8 hours** (with 2 parallel opportunities saving ~100 minutes)

---

## Parallel Opportunities

### Wave 5: platform_04 + platform_05 (Parallel)

Both workorders:
- Implement service detection (Windows + Linux)
- Have identical dependencies (all require platform.py extensions)
- Don't depend on each other
- **Process simultaneously** via Anthropic Batch API

Savings: ~40 minutes (both can run at same time)

### Wave 7: platform_07 + platform_08 (Parallel)

Both workorders:
- Implement service installation (Windows + Linux)
- Both depend on ServiceManager (platform_06)
- Don't depend on each other
- **Process simultaneously** via Anthropic Batch API

Savings: ~50 minutes (both can run at same time)

---

## Why This Approach?

### ✅ Benefits

1. **Respects Dependencies** — platform_01 won't run until platform_00 completes
2. **Maximizes Parallelism** — Runs platform_04+05 and platform_07+08 in parallel
3. **Cost-Efficient** — Batch API with 50% discount
4. **Reliable** — Anthropic API handles retries automatically
5. **Transparent** — Shows which workorders running at each stage

### ⚠️ Important Notes

1. **Wave Delays** — Script waits for each wave to complete before submitting next
   - This is necessary to respect dependencies
   - Anthropic Batch API processes waves in parallel automatically
2. **API Limits** — Within each wave, Anthropic API processes requests in parallel
3. **Polling Interval** — Script checks status every 5 seconds (configurable)

---

## Monitoring Progress

### During Execution

The script prints progress:

```
Waiting for batch 1/12 to complete...... ✓ DONE
```

Each dot is a 5-second poll. If you see many dots, batch is still processing (normal).

### Checking Status Manually

If the script is interrupted, you can check batch status:

```bash
python3 -c "
import anthropic
client = anthropic.Anthropic()
batch = client.beta.messages.batches.retrieve('batch_id_here')
print(f'Status: {batch.processing_status}')
print(f'Requests: {batch.request_counts.succeeded + batch.request_counts.errored}')
"
```

### Retrieving Results

If the script completes successfully, all results are displayed. If interrupted:

```bash
python3 -c "
import anthropic
client = anthropic.Anthropic()
for result in client.beta.messages.batches.results('batch_id_here'):
    print(result.custom_id, '→', 'SUCCESS' if hasattr(result.result, 'message') else 'ERROR')
"
```

---

## If Something Fails

### Batch Fails Completely

- Check API key is set: `echo \$ANTHROPIC_API_KEY`
- Check internet connection
- Retry the script (it will resume from the next wave)

### Individual Workorder Fails

- Script shows which workorder errored in the results summary
- Review the workorder file for issues
- Can resubmit just that workorder later

### Script Interrupted

- Results are saved to `logs/last_batch.txt`
- Can retrieve results manually using batch ID
- Re-running the script will start from the next wave

---

## After Completion

Once all waves complete:

1. **Review Results** — Script shows summary for each workorder
2. **Check Commits** — Each workorder should have created a commit
3. **Verify PRs** — Check if any PR reviews needed
4. **Next Steps** — Run integration tests or move to next phase

---

## Cost Breakdown (Actual)

Execution via `submit-platform-batch-parallel.py`:

```
Wave 1:  platform_00 (Haiku 4.5)     = ~$0.04
Wave 2:  platform_01 (Haiku 4.5)     = ~$0.05
Wave 3:  platform_02 (Haiku 4.5)     = ~$0.06
Wave 4:  platform_03 (Haiku 4.5)     = ~$0.04
Wave 5:  platform_04, 05 (Haiku 4.5) = ~$0.09 (parallel)
Wave 6:  platform_06 (Haiku 4.5)     = ~$0.05
Wave 7:  platform_07, 08 (Haiku 4.5) = ~$0.10 (parallel)
Wave 8:  platform_09 (Haiku 4.5)     = ~$0.05
Wave 9:  platform_10 (Haiku 4.5)     = ~$0.06
Wave 10: platform_11 (Haiku 4.5)     = ~$0.07
Wave 11: platform_12 (Opus 4.6)      = ~$0.17 (complex analysis)
Wave 12: platform_13 (Haiku 4.5)     = ~$0.10
────────────────────────────────────────────
Total:                                 ~$0.88 USD
```

*(Slightly higher than estimate due to verbose Opus output for EVOLUTION.md)*

---

## Debugging

### Enable Verbose Output

Edit script, add after line imports:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Submission (Single Workorder)

```bash
python3 -c "
import sys
sys.path.insert(0, '/c/csc/bin')
from submit_platform_batch_parallel import load_workorder, create_batch_request
content = load_workorder('platform_00')
request = create_batch_request('platform_00', content)
print('Request created successfully')
print(f'Model: {request[\"params\"][\"model\"]}')
print(f'Max tokens: {request[\"params\"][\"max_tokens\"]}')
"
```

---

## Reference

- **Script**: `bin/submit-platform-batch-parallel.py`
- **Configuration**: `workorders/batch/BATCH_SUBMISSION.md`
- **Dependencies**: Defined in script (DEPENDENCIES dict)
- **Models**: Haiku 4.5 (primary), Opus 4.6 (platform_12 only)
- **API**: Anthropic Batch API v1

