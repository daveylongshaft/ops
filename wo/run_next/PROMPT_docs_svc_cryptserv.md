# Document & Test: cryptserv service

## Task
1. Read `services/cryptserv_service.py` — document every public method
2. Add a `cryptserv` section to `docs/services.md` under "Security & Identity Services" (create if missing)
3. Write `tests/test_cryptserv_service.py`

## Documentation
- Document every command with syntax and description
- Explain what crypto operations are available
- Note any external dependencies (gpg, openssl subprocess calls, python libs)

## Tests
- Mock the server instance
- Test each crypto operation with known inputs/outputs
- Test error handling: bad input, missing dependencies
- Use `unittest.TestCase`
- File: `tests/test_cryptserv_service.py`

read services/cryptserv_service.py
read docs/services.md
update docs/services.md
write tests/test_cryptserv_service.py
check structure of docs/services.md
update docs/services.md
write tests/test_cryptserv_service.py
commit
move
push
