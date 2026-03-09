# Task: Fix Failing Test — queue_worker_temp_repo

## What Failed

Test file: `tests/test_queue_worker_temp_repo.py`
Log file: `tests/logs/test_queue_worker_temp_repo.log`

### FAILED lines

```
tests/test_queue_worker_temp_repo.py::TestGetAgentTempRepoCollision::test_fallback_path_collision_detected FAILED [ 46%]
tests/test_queue_worker_temp_repo.py::TestSpawnAgentSafety::test_spawns_in_isolated_repo FAILED [ 92%]
FAILED tests/test_queue_worker_temp_repo.py::TestGetAgentTempRepoCollision::test_fallback_path_collision_detected
FAILED tests/test_queue_worker_temp_repo.py::TestSpawnAgentSafety::test_spawns_in_isolated_repo
```

## Instructions

1. Read the full log at `tests/logs/test_queue_worker_temp_repo.log`
2. Identify root cause of each failure
3. Fix the **code under test**, not the test (unless the test itself is wrong)
4. `rm tests/logs/test_queue_worker_temp_repo.log` (so cron re-runs the test)
5. Commit, push, move this prompt to done. **Do NOT run pytest yourself.**
