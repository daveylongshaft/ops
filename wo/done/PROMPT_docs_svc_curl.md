# Document & Test: curl service

## Task
1. Read `services/curl_service.py` — document every public method
2. Add a `curl` section to `docs/services.md` under "Utility Services" (create if missing)
3. Write `tests/test_curl_service.py`

## Documentation
- Document every command with syntax
- Note the requests library dependency
- Explain any URL restrictions or safety measures

## Tests
- Mock the server instance
- Mock `requests.get`/`requests.post` — do NOT make real HTTP calls
- Test successful fetch, error responses, timeouts
- Test with missing/invalid URLs
- Use `unittest.TestCase`
- File: `tests/test_curl_service.py`

read services/curl_service.py
update docs/services.md
update docs/services.md
write tests/test_curl_service.py
commit
move
push
