# Test agent-wrapper implementation

## Task

Test the new universal agent-wrapper implementation (bin/agent-wrapper) introduced in commit e7c81bc.

Key areas to test:
1. Template copying functionality (copy_template_to_queue)
2. Queue mode flag support (--queue-mode)
3. Cross-platform script detection (Windows .bat/.exe, Unix)
4. Prompt movement between directories (ready → wip → done/ready)
5. Git operations (pull, add, commit, push)
6. Agent command building for different agent types
7. COMPLETE marker detection in WIP files
8. Pre-built prompt support via --use-file flag

## Work Log
