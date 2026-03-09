# Task: Fix Failing Test — cryptserv_service

## What Failed

Test file: `tests/test_cryptserv_service.py`
Log file: `tests/logs/test_cryptserv_service.log`

### FAILED lines

```
tests/test_cryptserv_service.py::TestCryptServ::test_request_new_cert FAILED [ 75%]
tests/test_cryptserv_service.py::TestCryptServ::test_requestor_not_found FAILED [100%]
FAILED tests/test_cryptserv_service.py::TestCryptServ::test_request_new_cert
FAILED tests/test_cryptserv_service.py::TestCryptServ::test_requestor_not_found
```

## Instructions

1. Read the full log at `tests/logs/test_cryptserv_service.log`
2. Identify root cause of each failure
3. Fix the **code under test**, not the test (unless the test itself is wrong)
4. Re-run: `python3 -m pytest tests/test_cryptserv_service.py -v > tests/logs/test_cryptserv_service.log 2>&1`
5. Verify zero FAILED lines in the new log
add import time to services/cryptserv_service.py
fix tests/test_cryptserv_service.py
delete log
commit
move
push
