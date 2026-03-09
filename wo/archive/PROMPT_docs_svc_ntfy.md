# Document & Test: ntfy service

## Task
1. Read `services/ntfy_service.py` — document every public method
2. Add an `ntfy` section to `docs/services.md` under "Utility Services" (create if missing)
3. Write `tests/test_ntfy_service.py`

## Documentation
- Document every command with syntax
- Explain ntfy.sh integration (push notifications)
- Note how topics/URLs are configured
- Note the curl dependency

## Tests
- Mock the server instance
- Mock subprocess.run (curl calls) — do NOT make real HTTP calls
- Test sending a notification, expected curl args
- Test error cases: missing topic, failed curl
- Use `unittest.TestCase`
- File: `tests/test_ntfy_service.py`

read services/ntfy_service.py
update docs/services.md
update docs/services.md
write tests/test_ntfy_service.py
commit
move
push
