# Prompts Queue System

Simple task management with crash recovery. Tasks flow through three directories.

## Quick Commands

```bash
# What am I working on?
prompts list wip
prompts read <filename>

# What's queued?
prompts list ready
prompts status

# Move to next task
prompts move <filename> wip

# When done, move to archive
prompts move <filename> done
```

## File Format

```
NN_short_description.md
```

Files contain PLANNING ONLY:
- Requirements and acceptance criteria
- Workflow steps
- **Work Log section at bottom (critical for crash recovery)**
- NO code, NO JSON snippets

Example work log:

```
PID: 184131 agent: claude starting at 2026-02-17 08:15
read version_service.py
read docs/services.md
add version docs to services.md
write tests/test_version_service.py
commit changes
push
move to done
```

## Work Log Rules

**Use `echo >>` to append one line per step BEFORE you do it. That's it.**

No checkboxes. No Edit tool. No re-reading. Just a flat list.

```bash
echo "read backup_service.py" >> /opt/csc/prompts/wip/TASK.md
echo "add backup docs to services.md" >> /opt/csc/prompts/wip/TASK.md
echo "write tests/test_backup_service.py" >> /opt/csc/prompts/wip/TASK.md
```

On crash: the next agent reads the WIP once, sees the last step logged, and resumes from there.

**NEVER run tests** — cron runs them within 1 minute for free.

## Task Dependencies

Some tasks depend on others. Check the requirements section:

Current chain:
```
Task 50 (DONE) → Task 51 → Task 52 → Task 53 → Task 54
```

Only start a task when its dependencies are done.

## Current Task Queue

### IN PROGRESS
None currently (wip/ is empty)

### NEXT UP
1. **Task 51** - Create csc-shared package
   - Depends: Task 50 (audit) - DONE
   - Agents: explore (understand current state), feature-implementer (build pyproject.toml)
   - Effort: Medium

2. **Task 52** - Restructure apps as packages
   - Depends: Task 51
   - Creates: csc-server, csc-client, csc-claude, csc-gemini, csc-chatgpt packages

3. **Task 53** - GitHub repo/directory split
   - Depends: Task 52
   - Splits single GitHub repo into 6 repos

4. **Task 54** - Packaging and portability
   - Depends: Task 53
   - Final packaging polish and pip installation

### READY (NO DEPENDENCIES)
- Task 01 - Verify Gemini communication
- Task 02 - Debug Gemini message handling
- Task 11 - Test topic command
- Task 42 - Testing, verification, documentation

### COMPLETED
Tasks 01-10 and related completed tasks in `done/`

## Workflow Example

1. **Start:** Check what's queued
   ```bash
   prompts list ready
   # Pick task 51
   prompts move 51_create_shared_package.md wip
   prompts read 51_create_shared_package.md
   ```

2. **Work:** Echo each step BEFORE you do it
   ```bash
   echo "read requirements" >> /opt/csc/prompts/wip/51_create_shared_package.md
   # ... read requirements ...
   echo "create pyproject.toml" >> /opt/csc/prompts/wip/51_create_shared_package.md
   # ... create file ...
   ```

3. **Crash:** Next agent reads the WIP, sees the last step logged, resumes from there.
   ```bash
   echo "--- RESTART $(date) ---" >> /opt/csc/prompts/wip/51_create_shared_package.md
   echo "resuming from pyproject.toml" >> /opt/csc/prompts/wip/51_create_shared_package.md
   ```

4. **Complete:** Task done
   ```bash
   prompts move 51_create_shared_package.md done
   git add -A
   git commit -m "Task 51: Create csc-shared package"
   git push
   ```

## Keeping WIP Current (Journal Style)

You don't need to read the WIP file except at session start. Use it as an append-only journal — echo a quick update before each step so the next agent picking up the task doesn't repeat your work.

```bash
echo "checked storage.py — atomic writes already handle channels.json" >> /opt/csc/prompts/wip/TASK.md
echo "add same pattern to opers.json" >> /opt/csc/prompts/wip/TASK.md
# Do the work...
echo "update bans.json handler" >> /opt/csc/prompts/wip/TASK.md
```

One line per step, BEFORE you do it. The next agent reads it once and picks up where you left off.

## Key Principles

- **Multiple agents OK** - Stamp PID so others know a WIP is live
- **Work log inside the file** - Not in separate logs
- **Crash markers** - So you can resume mid-task
- **Planning only** - No code in task files
- **Use lightest model** - Haiku for exploration, Sonnet for complex logic, Opus rarely

## Agent Recommendation Prefixes

Prompt filenames start with the recommended agent/model:

| Prefix | Model | Use For |
|--------|-------|---------|
| `haiku-` | Claude Haiku 4.5 | Lightweight: test validation, simple edits |
| `sonnet-` | Claude Sonnet 4.5 | Moderate: setup, debugging, multi-file changes |
| `opus-` | Claude Opus 4.6 | Critical: system design, architecture (rare) |
| `gemini-2.5-flash-light-` | Gemini 2.5 Flash Light | Practically free: trivial validation |
| `gemini-2.5-flash-` | Gemini 2.5 Flash | Fast, low resource tasks |
| `gemini-2.0-flash-` | Gemini 2.0 Flash | Straightforward container/setup tasks |
| `gemini-2.5-pro-` | Gemini 2.5 Pro | Moderate complexity code changes |
| `gemini-3.0-flash-` | Gemini 3.0 Flash | Fast reasoning, CI/CD design |
| `gemini-3.0-pro-` | Gemini 3.0 Pro | Complex reasoning, architecture |
| `docker-coder-` | Coding agent (Docker) | Must run inside Docker container |

## Platform-Gated Prompts

Prompts can declare platform requirements via YAML front-matter:

```yaml
---
requires: [docker, git]
platform: [windows]
min_ram: 4GB
---
```

The agent service checks these tags against `platform.json` before assignment. If the machine doesn't match, the prompt stays in `ready/` for the next machine.

## Directory Structure (DO NOT CREATE EXTRA DIRS)



The ONLY valid directories under `prompts/` are:



```

prompts/

├── ready/    # Queued tasks waiting to be worked on

├── wip/      # Current task (max 1 at a time)

├── done/     # Completed/archived tasks

├── hold/     # Tasks on hold - DO NOT WORK ON THESE

└── README.md # This file

```



**CRITICAL RULES:**

- **Hold Directory:** Prompts in the `hold/` directory are NOT to be worked on. They are parked for architectural or strategic reasons.

- **Dead Ends:** Any prompt file that ends with the text `DEAD END` is not to be resumed or processed further.



**NEVER create `prompts/prompts.wip/`, `prompts/prompts.ready/`, or any other subdirectory.**

 Use the existing `wip/`, `ready/`, and `done/` directories only. The `prompts` CLI command manages these three directories — extra dirs will cause confusion and duplicated work.

## Automated Test Runner (Cron)

The test system generates prompts automatically. **Do not run tests manually** — the cron runner handles it.

### How It Works

```
tests/run_tests.sh  →  scans tests/test_*.py
                    →  skips any with existing tests/logs/<name>.log
                    →  runs missing tests, always creates log
                    →  if FAILED lines in log → creates prompts/ready/PROMPT_fix_test_<name>.md
```

### The Cycle

1. **Cron runs** `tests/run_tests.sh`
2. For each `tests/test_*.py` **without** a matching `tests/logs/*.log`:
   - Runs the test, creates the log (pass or fail)
   - **If PLATFORM_SKIP lines exist** → deletes the log (retry on right platform)
   - If FAILED lines exist → fills `tests/prompt_template.md` → writes `prompts/ready/PROMPT_fix_test_<name>.md`
3. AI picks up the fix prompt, fixes the code
4. **Human deletes the log** to allow re-testing
5. Next cron run retests (back to step 2)

### Cross-Platform Tests

Tests targeting a specific platform use `tests/platform_gate.py`:
```python
from platform_gate import require_platform
require_platform(["windows"])  # Prints PLATFORM_SKIP on non-Windows
```

When cron runs a platform-gated test on the wrong machine:
1. Log **stays** (locks this machine from re-running it)
2. Cron generates `PROMPT_run_test_<name>.md` — a routing prompt
3. Prompt flows via git to other machines
4. AI on the right platform picks it up, deletes the log, lets cron re-run the test there

### Key Rules

- **Log file = lock.** If `tests/logs/test_foo.log` exists, the test is NOT re-run and NO new prompt is created.
- **Delete a log to force retest.** This is how you trigger a re-run after a fix.
- **Never run tests manually.** The cron runner is idempotent and handles everything.
- **One test file at a time.** No shotgun `pytest tests/` runs.
- **Template:** `tests/prompt_template.md` — contains placeholders for test name, failed lines, and log path.

### Files

| File | Purpose |
|------|---------|
| `tests/run_tests.sh` | Cron-driven test runner script |
| `tests/prompt_template.md` | Template for auto-generated fix prompts |
| `tests/logs/*.log` | Test output logs (lock files) |

See `/opt/csc/README.1st` for full system details and cost efficiency guidelines.
