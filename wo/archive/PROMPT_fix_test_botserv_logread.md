# Task: Fix Failing Test — botserv_logread

## What Failed

Test file: `tests/test_botserv_logread.py`
Log file: `tests/logs/test_botserv_logread.log`

### FAILED lines

```
tests/test_botserv_logread.py::TestBotservLogread::test_logread_incremental_read_success FAILED [ 63%]
tests/test_botserv_logread.py::TestBotservLogread::test_logread_initial_read_success FAILED [ 68%]
tests/test_botserv_logread.py::TestBotservLogread::test_logread_no_new_lines FAILED [ 72%]
tests/test_botserv_logread.py::TestBotservLogread::test_logread_with_argument_filter_match FAILED [ 77%]
tests/test_botserv_logread.py::TestBotservLogread::test_logread_with_argument_filter_no_match FAILED [ 81%]
tests/test_botserv_logread.py::TestBotservLogread::test_logread_with_both_channel_filters_and_argument_filter FAILED [ 86%]
tests/test_botserv_logread.py::TestBotservLogread::test_logread_with_channel_match_filter FAILED [ 90%]
tests/test_botserv_logread.py::TestBotservLogread::test_logread_with_channel_nomatch_filter FAILED [ 95%]
tests/test_botserv_logread.py::TestBotservLogread::test_logread_with_invalid_argument_filter_pattern FAILED [100%]
FAILED tests/test_botserv_logread.py::TestBotservLogread::test_logread_incremental_read_success
FAILED tests/test_botserv_logread.py::TestBotservLogread::test_logread_initial_read_success
FAILED tests/test_botserv_logread.py::TestBotservLogread::test_logread_no_new_lines
FAILED tests/test_botserv_logread.py::TestBotservLogread::test_logread_with_argument_filter_match
FAILED tests/test_botserv_logread.py::TestBotservLogread::test_logread_with_argument_filter_no_match
FAILED tests/test_botserv_logread.py::TestBotservLogread::test_logread_with_both_channel_filters_and_argument_filter
FAILED tests/test_botserv_logread.py::TestBotservLogread::test_logread_with_channel_match_filter
FAILED tests/test_botserv_logread.py::TestBotservLogread::test_logread_with_channel_nomatch_filter
FAILED tests/test_botserv_logread.py::TestBotservLogread::test_logread_with_invalid_argument_filter_pattern
```

## Instructions

1. Read the full log at `tests/logs/test_botserv_logread.log`
2. Identify root cause of each failure
3. Fix the **code under test**, not the test (unless the test itself is wrong)
4. `rm tests/logs/test_botserv_logread.log` (so cron re-runs the test)
5. Commit, push, move this prompt to done. **Do NOT run pytest yourself.**
