You are building and submitting a Claude Haiku batch job to generate pytest test files. Work entirely in /opt/audit/. Journal every step to this file before doing it.

## Setup

```bash
mkdir -p /opt/audit/ops/wo/wip
mv /opt/audit/ops/wo/ready/batch-write-tests.md /opt/audit/ops/wo/wip/batch-write-tests.md
echo "PID: $$ starting at $(date)" >> /opt/audit/ops/wo/wip/batch-write-tests.md
```

Load the API key:
```bash
source <(grep ANTHROPIC_API_KEY /opt/csc/.env | sed 's/^/export /')
```

## Step 1 — Build the batch JSONL

Write a Python script `/opt/audit/build_batch.py` that:

1. Walks every `test_*.py` in `/opt/audit/csc_old/tests/` — skip `live_*.py` (require live server)
2. For each old test, finds the corresponding module under `/opt/audit/irc/packages/csc-service/csc_service/` by stripping `test_` prefix and searching for that filename
3. Builds one batch request entry per test:
   - `custom_id`: stem of test file (e.g. `test_server_irc`)
   - `model`: `claude-haiku-4-5-20251001`
   - `max_tokens`: 4096
   - System prompt: (see below)
   - User message: old test content + new module content (truncated to 6000 chars each if needed)
4. Writes `/opt/audit/batch_requests.json` — a JSON object `{"requests": [...]}`

System prompt to embed in each request:
```
You are writing a pytest test file for a Python module that is part of a CSC (Client-Server Commander) IRC orchestration system.

Rules:
- Use pytest, not unittest
- Mock external dependencies (network, file I/O, subprocess) with unittest.mock
- Do NOT hardcode any absolute paths - use tmp_path fixture or monkeypatch
- Do NOT call Data(), Log(), Platform() with real paths - mock them
- Test the module's key functions/classes
- Keep tests self-contained and fast (no live network, no live server)
- File must be importable standalone
- Permissions on new files: the test runner handles this
- Output ONLY the Python test file content, no explanation
```

User message template per request:
```
Write a pytest test file for this module.

## Old test (reference for what to cover):
<old test content, max 6000 chars>

## New module to test (source of truth):
Path: <new module path relative to irc/>
<new module content, max 6000 chars>

Output only the complete test file content.
```

If no corresponding new module exists for an old test, include the request anyway using only the old test as reference — write tests that match what *would* exist in the new architecture.

Run the script:
```bash
python3 /opt/audit/build_batch.py
```

Verify output:
```bash
python3 -c "import json; d=json.load(open('/opt/audit/batch_requests.json')); print(f'{len(d[\"requests\"])} requests built')"
```

## Step 2 — Submit the batch

```bash
curl -s https://api.anthropic.com/v1/messages/batches \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: message-batches-2024-09-24" \
  -H "content-type: application/json" \
  -d @/opt/audit/batch_requests.json \
  | tee /opt/audit/batch_response.json | python3 -c "import json,sys; r=json.load(sys.stdin); print('batch_id:', r.get('id')); print('status:', r.get('processing_status'))"
```

Save the batch ID:
```bash
python3 -c "import json; r=json.load(open('/opt/audit/batch_response.json')); open('/opt/audit/batch_id.txt','w').write(r['id'])"
echo "Batch ID saved: $(cat /opt/audit/batch_id.txt)"
```

## Step 3 — Write the retrieval script

Write `/opt/audit/retrieve_batch.py`:

```python
#!/usr/bin/env python3
"""
Retrieve Claude batch results and write test files to irc/tests/.

Usage:
    python3 /opt/audit/retrieve_batch.py

Reads batch ID from /opt/audit/batch_id.txt.
Polls until complete, then writes each result to /opt/audit/irc/tests/<custom_id>.py
"""
import os, json, time, urllib.request, urllib.error
from pathlib import Path

BATCH_ID_FILE = Path("/opt/audit/batch_id.txt")
OUT_DIR = Path("/opt/audit/irc/tests")
ENV_FILE = Path("/opt/csc/.env")

def load_env():
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

def api_get(path):
    key = os.environ["ANTHROPIC_API_KEY"]
    req = urllib.request.Request(
        f"https://api.anthropic.com/v1/{path}",
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "anthropic-beta": "message-batches-2024-09-24",
        }
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def main():
    load_env()
    batch_id = BATCH_ID_FILE.read_text().strip()
    print(f"Polling batch {batch_id}...")

    while True:
        status = api_get(f"messages/batches/{batch_id}")
        ps = status.get("processing_status")
        counts = status.get("request_counts", {})
        print(f"  status={ps} counts={counts}")
        if ps == "ended":
            break
        time.sleep(30)

    # Fetch results
    results_url = status.get("results_url")
    req = urllib.request.Request(results_url, headers={
        "x-api-key": os.environ["ANTHROPIC_API_KEY"],
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "message-batches-2024-09-24",
    })
    with urllib.request.urlopen(req) as r:
        lines = r.read().decode().strip().splitlines()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    for line in lines:
        result = json.loads(line)
        custom_id = result["custom_id"]
        if result.get("result", {}).get("type") == "succeeded":
            content = result["result"]["message"]["content"][0]["text"]
            out_file = OUT_DIR / f"{custom_id}.py"
            out_file.write_text(content, encoding="utf-8")
            os.chmod(out_file, 0o664)
            print(f"  wrote {out_file.name}")
            written += 1
        else:
            print(f"  FAILED: {custom_id} — {result.get('result', {}).get('error')}")

    print(f"\nDone: {written}/{len(lines)} tests written to {OUT_DIR}")

if __name__ == "__main__":
    main()
```

## Step 4 — Commit scripts and close WO

```bash
cd /opt/audit/ops
git add wo/
git commit -m "wo: batch-write-tests submitted, batch_id=$(cat /opt/audit/batch_id.txt)"
git push

mv /opt/audit/ops/wo/wip/batch-write-tests.md /opt/audit/ops/wo/done/
git add wo/
git commit -m "wo: batch-write-tests done"
git push
```

Append final line:
```bash
echo "COMPLETE — batch $(cat /opt/audit/batch_id.txt) submitted. Run: python3 /opt/audit/retrieve_batch.py when ready." >> /opt/audit/ops/wo/done/batch-write-tests.md
```

## Notes

- Do NOT run the retrieval script — batch takes ~15 min to process
- Do NOT run pytest
- build_batch.py and retrieve_batch.py stay in /opt/audit/ (not committed to irc)
- The retrieval script can be run anytime after the batch ends
PID: 2974039 starting at Mon 09 Mar 2026 05:53:34 PM CDT
COMPLETE — batch msgbatch_01LKEmGPG1aYGbUZSQV6WjiE submitted. Run: python3 /opt/audit/retrieve_batch.py when ready.
