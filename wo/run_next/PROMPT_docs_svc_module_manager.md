# Document & Test: module_manager service

## Task
1. Read `services/module_manager_service.py` — document every public method
2. Add/update the `module_manager` section in `docs/services.md`
3. Write `tests/test_module_manager_service.py`

## Documentation
For each public method, document:
- Command syntax: `AI <token> module_manager <method> [args]`
- What it does, what it returns
- The staging/approval/rehash workflow

## Tests
- Follow the pattern in `tests/test_patch_service.py` for imports and structure
- Mock the server instance
- Test list, staging, approve, rehash with mocked filesystem
- Test error cases: missing module, bad name
- Use `unittest.TestCase`
- File: `tests/test_module_manager_service.py`

read services/module_manager_service.py
update docs/services.md
update docs/services.md
write tests/test_module_manager_service.py
commit
move
push
