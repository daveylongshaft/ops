# Document & Test: nickserv service

## Task
1. Read `services/nickserv_service.py` — document every public method
2. Add a `nickserv` section to `docs/services.md` under a new "Security & Identity Services" heading (create if missing)
3. Write `tests/test_nickserv_service.py`

## Documentation
- Document every command: REGISTER, IDENTIFY, GHOST, DROP, INFO, SET, etc.
- Explain the credential storage model (where passwords are stored, hashing)
- Note integration with server user/oper system
- Command syntax: `AI <token> nickserv <method> [args]`

## Tests
- Mock the server instance and its storage (users.json, opers.json)
- Test registration flow: register, identify, ghost
- Test error cases: duplicate registration, wrong password, unregistered nick
- Test INFO and SET commands
- Use `unittest.TestCase`, use tempdir for any JSON files
- File: `tests/test_nickserv_service.py`

Note: `tests/test_nickserv.py` already exists and tests the server-level NickServ handler. This new file tests the service module directly.

read services/nickserv_service.py
update docs/services.md
update docs/services.md
write tests/test_nickserv_service.py
commit
move
push
