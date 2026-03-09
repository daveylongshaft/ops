# Prompt: Regenerate tools/ Code Maps

## Goal

After all docstring prompts are complete, regenerate the `tools/` directory to produce the fully documented developer code maps.

## Prerequisites

All four docstring prompts must be done first:
- PROMPT_docstrings_01_packages.md
- PROMPT_docstrings_02_bridge.md
- PROMPT_docstrings_03_services_and_root.md
- PROMPT_docstrings_04_tests.md

## Steps

### 1. Verify zero undocumented items

```bash
cd /opt/csc && python3 analyze_project.py
```

Expected output should show `0 undocumented`. If not, check `analysis_report.json` for remaining items and fix them before proceeding.

### 2. Review the generated tools/ files

```bash
ls -la /opt/csc/tools/
```

Read `tools/INDEX.txt` — verify all packages are listed with correct class/function counts.

Spot-check 2-3 package files (e.g. `tools/csc-server.txt`, `tools/csc-shared.txt`) to confirm docstring summaries appear next to every method signature.

### 3. Verify the code maps are useful

For each package file in `tools/`, confirm:
- Every `def` line has a `# summary` comment after it (from the docstring first line)
- No methods show up without documentation
- Class docstrings appear as `# summary` after the class line

### 4. Fix any gaps

If any methods still show no `# summary`, the docstring is either missing or doesn't have a first line the analyzer can extract. Fix the docstring in the source file, then re-run `analyze_project.py`.

### 5. Done

The `tools/` directory is now the complete developer headstart — read `INDEX.txt`, pick a package, read the map, then go to the source file. No more reading raw code to understand the codebase.

## Deliverable

- `tools/INDEX.txt` and all `tools/*.txt` files regenerated with full documentation
- `analysis_report.json` shows empty list (`[]`)
- Log this work in `/opt/csc/contrib.txt`

Verified complete.
