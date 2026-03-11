# Document & Test: backup service

## Task
1. Read `services/backup_service.py` — document every public method
2. Add a `backup` section to `docs/services.md` under a new "Utility Services" heading (create if missing)
3. Write `tests/test_backup_service.py`

## Documentation
- Document every command with syntax
- Explain what gets backed up, where backups go, format (tar, etc.)
- Note any diff/restore capabilities

## Tests
- Mock the server instance
- Test backup creation with temp dirs and files
- Test listing/restoring backups if those methods exist
- Test error cases: missing paths, permission issues
- Use `unittest.TestCase`, use tempdir
- File: `tests/test_backup_service.py`


### Agent Session (2026-02-17 07:53:58)
- Agent: claude
- [NEXT] Agent starting work
Agent starting: Tue 17 Feb 2026 07:54:28 AM GMT
read services/backup_service.py
read docs/services.md to check current structure
add backup service docs to docs/services.md
write tests/test_backup_service.py
commit and push changes
move prompt to done
