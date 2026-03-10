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
