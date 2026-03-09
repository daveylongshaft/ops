# Document & Test: patch service

## Task
1. Read `services/patch_service.py` — document every public method
2. Add a `patch` section to `docs/services.md` under "Workflow & Automation Services" (create if missing)
3. Write additional tests in `tests/test_patch_service.py` if coverage is lacking (tests already exist — read them first, only add what's missing)

## Documentation
- Document every command with syntax
- Explain the fuzzy matching / loose-format patcher
- Explain how anchors and hunks work
- Note limitations and edge cases

## Tests
- `tests/test_patch_service.py` already exists — read it first
- Only add tests for methods or edge cases NOT already covered
- If fully covered, note that in the WIP journal and skip

read services/patch_service.py
read tests/test_patch_service.py
update docs/services.md
update tests/test_patch_service.py
rewrite tests/test_patch_service.py with new tests
commit
move
push
