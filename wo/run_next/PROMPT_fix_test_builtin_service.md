# Task: Fix Failing Test — builtin_service

## What Failed

Test file: `tests/test_builtin_service.py`
Log file: `tests/logs/test_builtin_service.log`

### FAILED lines

```
tests/test_builtin_service.py::TestBuiltinService::test_ftp_connect_list FAILED [ 57%]
tests/test_builtin_service.py::TestBuiltinService::test_ftp_download_file FAILED [ 64%]
tests/test_builtin_service.py::TestBuiltinService::test_ftp_upload_file FAILED [ 71%]
tests/test_builtin_service.py::TestBuiltinService::test_list_dir FAILED  [ 78%]
tests/test_builtin_service.py::TestBuiltinService::test_move_local FAILED [ 85%]
FAILED tests/test_builtin_service.py::TestBuiltinService::test_ftp_connect_list
FAILED tests/test_builtin_service.py::TestBuiltinService::test_ftp_download_file
FAILED tests/test_builtin_service.py::TestBuiltinService::test_ftp_upload_file
FAILED tests/test_builtin_service.py::TestBuiltinService::test_list_dir - Ass...
FAILED tests/test_builtin_service.py::TestBuiltinService::test_move_local - A...
```

## Instructions

1. Read the full log at `tests/logs/test_builtin_service.log`
2. Identify root cause of each failure
3. Fix the **code under test**, not the test (unless the test itself is wrong)
4. Re-run: `python3 -m pytest tests/test_builtin_service.py -v > tests/logs/test_builtin_service.log 2>&1`
5. Verify zero FAILED lines in the new log
fix tests/test_builtin_service.py
delete log
commit
move
push
