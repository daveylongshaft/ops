# Task: Fix Failing Test — csc_ctl

## What Failed

Test file: `tests/test_csc_ctl.py`
Log file: `tests/logs/test_csc_ctl.log`

### FAILED lines

```
tests/test_csc_ctl.py::TestCscCtl::test_csc_ctl_config_get FAILED        [ 14%]
tests/test_csc_ctl.py::TestCscCtl::test_csc_ctl_config_set FAILED        [ 28%]
tests/test_csc_ctl.py::TestCscCtl::test_csc_ctl_dump_all FAILED          [ 42%]
tests/test_csc_ctl.py::TestCscCtl::test_csc_ctl_dump_service FAILED      [ 57%]
tests/test_csc_ctl.py::TestCscCtl::test_csc_ctl_import FAILED            [ 71%]
tests/test_csc_ctl.py::TestCscCtl::test_csc_ctl_show FAILED              [ 85%]
tests/test_csc_ctl.py::TestCscCtl::test_csc_ctl_status FAILED            [100%]
FAILED tests/test_csc_ctl.py::TestCscCtl::test_csc_ctl_config_get - Assertion...
FAILED tests/test_csc_ctl.py::TestCscCtl::test_csc_ctl_config_set - Assertion...
FAILED tests/test_csc_ctl.py::TestCscCtl::test_csc_ctl_dump_all - AssertionEr...
FAILED tests/test_csc_ctl.py::TestCscCtl::test_csc_ctl_dump_service - Asserti...
FAILED tests/test_csc_ctl.py::TestCscCtl::test_csc_ctl_import - AssertionErro...
FAILED tests/test_csc_ctl.py::TestCscCtl::test_csc_ctl_show - AssertionError:...
FAILED tests/test_csc_ctl.py::TestCscCtl::test_csc_ctl_status - AssertionErro...
```

## Instructions

1. Read the full log at `tests/logs/test_csc_ctl.log`
2. Identify root cause of each failure
3. Fix the **code under test**, not the test (unless the test itself is wrong)
4. `rm tests/logs/test_csc_ctl.log` (so cron re-runs the test)
5. Commit, push, move this prompt to done. **Do NOT run pytest yourself.**
