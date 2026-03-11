---
urgency: P2
agent: sonnet
requires: python,google-genai,api-integration
tags: batch-api,async,polling
blockedBy: gemini-api-workflows-01-converter.md
---

# Workorder: Gemini Batch API - Async Batch Runner

## Context
Implement the async batch submission and polling workflow for Google Batch API. This is the 50% cheaper mode: upload JSONL, poll for results, download when complete. No tool execution (text-only responses).

**Related:** Part 4 of 12-part series. Blocked by workorder 01. Unblocks workorder 08.

## Deliverables

### Create `bin/gemini-batch/gbatch_run.py`

**CLI Usage:**
```
gbatch_run.py submit <requests.jsonl> [--model gemini-2.5-flash] [--cache]
gbatch_run.py status <job_name>
gbatch_run.py retrieve <job_name> [--out results.jsonl]
gbatch_run.py run <batch_config.json> [--agent gemini] [--cache]
```

### 1. `submit` Command
**Purpose:** Upload JSONL and submit batch job.

**Process:**
1. Read JSONL file, parse each line (validate structure)
2. Get Gemini API key via `common.get_gemini_api_key()`
3. Create client: `client = google.genai.Client(api_key=key)`
4. Upload JSONL file:
   ```python
   file_response = client.files.upload(file=open(jsonl_path, 'rb'))
   file_uri = file_response.uri  # e.g., "files/abc123def456"
   ```
5. If `--cache`: Get cached content name from `CacheManager` (workorder 07), embed in request
6. Submit batch:
   ```python
   batch = client.batches.create(
       model=model_name,  # e.g., "models/gemini-2.5-flash"
       input_config=InputConfig(
           contents=[BatchInput(request={"model": model, ...})] or file=file_uri
       ),
       timeout=Timedelta(seconds=86400)  # 24 hours
   )
   job_name = batch.name  # "batchOperations/abc123"
   ```
7. Save job metadata to `batch_state.json` in `bin/gemini-batch/`:
   ```json
   {
     "job_name": "batchOperations/abc123",
     "model": "gemini-2.5-flash",
     "entry_count": 42,
     "input_file_uri": "files/abc123def456",
     "submitted_at": "2026-03-03T12:34:56Z",
     "status": "QUEUED"
   }
   ```
8. Print: `"Submitted batch <job_name> with 42 requests. Model: gemini-2.5-flash. Use 'gbatch_run status <job_name>' to check."`

### 2. `status` Command
**Purpose:** Check job progress without retrieving results.

**Process:**
1. Get API key, create client
2. Retrieve batch: `batch = client.batches.get(name=job_name)`
3. Print:
   - Job name, model, submission time
   - Current state (QUEUED, IN_PROGRESS, COMPLETED, FAILED)
   - Progress: `"<completed>/<total> requests processed"`
   - ETA if in progress (based on completion rate)
4. If COMPLETED: print retrieval command

### 3. `retrieve` Command
**Purpose:** Download results when job completes.

**Process:**
1. Get job metadata from `batch_state.json` (or accept `--job-name` param)
2. Get API key, create client
3. Check status: `batch = client.batches.get(name=job_name)`
4. If not COMPLETED: print message with status and ETA, exit
5. Download results:
   ```python
   results_list = client.batches.get(name=job_name).results
   # or stream: for result in client.batches.stream_results(job_name):
   ```
6. Write results to JSONL (format per workorder 01):
   ```json
   {"key": "entry-001", "response": {...}}
   ```
7. Save to `batch_results_<timestamp>.jsonl` (e.g., `batch_results_20260303_123456.jsonl`)
8. Delete input file if requested (optional)
9. Update `batch_state.json` with `"status": "COMPLETED"`, `"retrieved_at": "...", "results_file": "..."`
10. Print: `"Retrieved 42 results. 40 succeeded, 2 failed. Saved to batch_results_20260303_123456.jsonl"`

**Cost reporting:**
- For each result, extract token counts from response metadata
- Sum input tokens × $0.15/M, output tokens × $1.25/M (50% batch discount applied)
- Print: `"Token cost: input=$X, output=$Y, total=$Z (batch rate)"`

### 4. `run` Command
**Purpose:** One-shot: convert config → submit → poll → retrieve.

**Process:**
1. Load `batch_config.json` via `common.load_config(path)`
2. Filter entries with `"provider": "gemini"`
3. Convert to Gemini JSONL via workorder 01 converter logic
4. Call `submit` logic → get `job_name`
5. Poll `status` in loop (30s intervals, exponential backoff):
   - Poll up to 10 times (5 minutes)
   - If complete: break
   - If still queued: print progress dot, continue
   - If timeout after 5 min: print message, save job name, exit (user can check manually)
6. When complete: call `retrieve` logic
7. Convert results back to markdown via converter (workorder 01) `from-results`
8. Print summary: N succeeded, N failed, total cost

**Optional flags:**
- `--agent gemini`: log which agent this is for (informational)
- `--cache`: use cached content from workorder 07
- `--async`: submit and exit (don't poll)

### Error Handling
- Network errors: retry up to 3 times with exponential backoff
- File upload failure: print error, suggest re-running
- API key missing: clear error message pointing to `GOOGLE_API_KEY` env var or config
- Batch API quota: print rate limit message, suggest time to retry
- Invalid JSONL: print first bad line, reject

## Testing Notes
- Unit test: `test_batch_config_submit()` — mock file upload + batch create, verify state saved
- Unit test: `test_batch_polling_complete()` — mock completed batch, verify retrieval
- Unit test: `test_batch_polling_timeout()` — mock queued batch >5 min, verify graceful exit
- Unit test: `test_cost_calculation()` — verify token math and batch discount applied

## Notes
- Does NOT execute tools (batch API is text-only; tool execution is workorder 04)
- Depends on workorder 01 for converter logic
- Workorder 07 (cache) is optional; can submit without caching
- All paths relative to `/c/csc/`
