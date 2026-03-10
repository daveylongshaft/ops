---
urgency: P2
tags: infrastructure,utility,data-analysis
requires: [python3]
---

# Create File Comparison Script: Date/Size Analysis for Valuable Data

## Objective

Create a Python script that compares files between `/c/csc/remainder/` and files in the live codebase to identify potentially valuable data by date modified and file size.

Purpose: Identify which files in `remainder/` contain data worth preserving that differs from the live codebase.

## Scope

Compare each file in `/c/csc/remainder/` with corresponding files in `/c/csc/` (or related directories) by:
1. **Date modified** - newer files likely have recent changes
2. **File size** - significant size differences indicate content changes
3. **File type** - prioritize config files, credentials, runtime state
4. **Not in codebase** - files that don't exist in live codebase are potentially valuable

## Deliverable

Create `/c/csc/ops/wo/compare_remainder_files.py`:

```python
#!/usr/bin/env python3
"""
Compare files in remainder/ directory with live codebase.
Identify valuable data by date and size differences.
"""
import os
import json
from pathlib import Path
from datetime import datetime

REMAINDER_DIR = Path("/c/csc/remainder")
CSC_ROOT = Path("/c/csc")

def get_file_info(path):
    """Get file metadata"""
    try:
        stat = path.stat()
        return {
            "path": str(path),
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "mtime_readable": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    except:
        return None

def compare_files():
    """Compare remainder files with live codebase"""
    results = {
        "newer_than_live": [],
        "different_size": [],
        "not_in_codebase": [],
        "identical": []
    }

    for remainder_file in REMAINDER_DIR.rglob("*"):
        if not remainder_file.is_file():
            continue

        rel_path = remainder_file.relative_to(REMAINDER_DIR)
        live_file = CSC_ROOT / rel_path

        remainder_info = get_file_info(remainder_file)
        if not remainder_info:
            continue

        if not live_file.exists():
            results["not_in_codebase"].append({
                "file": str(rel_path),
                "remainder_info": remainder_info
            })
        else:
            live_info = get_file_info(live_file)
            if remainder_info["size"] != live_info["size"]:
                results["different_size"].append({
                    "file": str(rel_path),
                    "remainder": remainder_info,
                    "live": live_info
                })
            elif remainder_info["mtime"] > live_info["mtime"]:
                results["newer_than_live"].append({
                    "file": str(rel_path),
                    "remainder": remainder_info,
                    "live": live_info
                })
            else:
                results["identical"].append(str(rel_path))

    return results

if __name__ == "__main__":
    print("Comparing remainder/ files with live codebase...")
    results = compare_files()

    print(f"\nNot in codebase: {len(results['not_in_codebase'])}")
    for item in results['not_in_codebase'][:10]:
        print(f"  - {item['file']} ({item['remainder_info']['size']} bytes)")

    print(f"\nDifferent size: {len(results['different_size'])}")
    for item in results['different_size'][:10]:
        print(f"  - {item['file']}")
        print(f"    Remainder: {item['remainder']['size']} bytes")
        print(f"    Live: {item['live']['size']} bytes")

    print(f"\nNewer in remainder: {len(results['newer_than_live'])}")
    for item in results['newer_than_live'][:10]:
        print(f"  - {item['file']}")
        print(f"    Remainder: {item['remainder']['mtime_readable']}")
        print(f"    Live: {item['live']['mtime_readable']}")

    # Write full results to JSON
    output_file = CSC_ROOT / "logs" / "remainder_comparison_results.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nFull results saved to: {output_file}")
```

## Usage

```bash
python3 /c/csc/ops/wo/compare_remainder_files.py
```

Output:
- Displays summary to console
- Writes detailed JSON to `/c/csc/logs/remainder_comparison_results.json`

## Expected Output

JSON with categories:
- `not_in_codebase` - Files unique to remainder/ (high value)
- `different_size` - Size mismatch (likely changed content)
- `newer_than_live` - Modified more recently (changes present)
- `identical` - Same as live codebase (safe to discard)

Use results to decide what to preserve from `remainder/`.

## Verification

- [ ] Script runs without errors
- [ ] Creates JSON output file
- [ ] Identifies .env, config files, and credentials
- [ ] Shows size/date differences clearly
- [ ] Can be committed to git

COMPLETE


--- Agent Log ---
Already up to date.
Current branch main is up to date.
Invoking: gemini -y -m gemini-2.5-pro -p " " (cwd: /opt, repo: /opt/csc/tmp/gemini-2.5-pro/create_file_comparison_script-1773112753/repo)
[WARN] Skipping unreadable directory: /opt/csc/.config/configstore (EACCES: permission denied, scandir '/opt/csc/.config/configstore')
YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
[WARN] Skipping unreadable directory: /opt/csc/.config/configstore (EACCES: permission denied, scandir '/opt/csc/.config/configstore')
YOLO mode is enabled. All tool calls will be automatically approved.
Hook registry initialized with 0 hook entries
Error when talking to Gemini API Full report available at: /tmp/gemini-client-error-Turn.run-sendMessageStream-2026-03-10T03-19-40-181Z.json TerminalQuotaError: You have exhausted your capacity on this model. Your quota will reset after 15h25m14s.
    at classifyGoogleError (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/googleQuotaErrors.js:214:28)
    at retryWithBackoff (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/retry.js:131:37)
    at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
    at async GeminiChat.makeApiCallAndProcessStream (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:431:32)
    at async GeminiChat.streamWithRetries (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:263:40)
    at async Turn.run (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/turn.js:66:30)
    at async GeminiClient.processTurn (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/client.js:459:26)
    at async GeminiClient.sendMessageStream (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/client.js:559:20)
    at async file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/dist/src/nonInteractiveCli.js:193:34
    at async main (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/dist/src/gemini.js:492:9) {
  cause: {
    code: 429,
    message: 'You have exhausted your capacity on this model. Your quota will reset after 15h25m14s.',
    details: [ [Object], [Object] ]
  },
  retryDelayMs: 55514873.484185
}
An unexpected critical error occurred:[object Object]

[INFO] Agent execution completed
[INFO] Log: /opt/csc/ops/logs/gemini-2.5-pro_1773112754.log
