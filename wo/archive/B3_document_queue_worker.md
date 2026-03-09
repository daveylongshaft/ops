# Phase B3: Document Queue Worker System

## Task

Create documentation for the queue worker system explaining architecture and usage.

## Requirements

**File:** `docs/queue_worker.md`

Documentation should cover:
1. Architecture overview
2. How queue system works
3. Directory structure
4. PID tracking mechanism
5. Scheduling setup (Windows/Linux)
6. Troubleshooting guide
7. Monitoring queue status

## Content Structure

```markdown
# Queue Worker System

## Overview
Background service that processes agent task queues.

## Architecture
- Queue directories: agents/*/queue/{in,work}
- Periodic execution via Task Scheduler (Windows) or cron (Linux)
- Non-blocking: spawns wrappers, exits, checks completion later

## How It Works
1. Scan queue/in/ for new prompts
2. Move to queue/work/ and spawn wrapper
3. Save wrapper PID to .pid file
4. On next run, check if PID is dead
5. Process completed work, archive results

## Directory Structure
[Explain agents/*/queue layout]

## Setup
[Windows Task Scheduler commands]
[Linux crontab commands]

## Monitoring
[How to check queue status]
[Log file locations]

## Troubleshooting
[Common issues and solutions]
```

## Acceptance

- Documentation complete and clear
- Examples provided
- Troubleshooting section helpful
- Architecture diagram (optional)

## Work Log
1. Document queue worker
Queue worker service documented in csc-shared/services/
