# Document & Test: builtin service

## Task
1. Read `services/builtin_service.py` — document every public method
2. Add/update the `builtin` section in `docs/services.md` under "Built-in Management Services"
3. Write `tests/test_builtin_service.py` with unit tests for each method

## Documentation
For each public method, document:
- Command syntax: `AI <token> builtin <method> [args]`
- What it does, what it returns
- Any restrictions (path confinement, permissions)

## Tests
- Follow the pattern in `tests/test_patch_service.py` for imports and structure
- Mock the server instance (services expect `server_instance` in `__init__`)
- Test each public method with representative inputs
- Test edge cases: missing args, invalid paths, boundary conditions
- Use `unittest.TestCase`, no pytest fixtures
- File: `tests/test_builtin_service.py`


read services/builtin_service.py
read docs/services.md
update builtin section in docs/services.md
write tests/test_builtin_service.py
update tests/test_builtin_service.py with FTP tests
verify changes
commit changes
move to done
push
