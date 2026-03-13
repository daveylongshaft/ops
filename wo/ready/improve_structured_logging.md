# Implement Structured Logging with Rotation

**Priority**: P3 (observability)
**Estimate**: 4 hours
**Assignee**: jules | codex | gemini
**Reviewer**: anthropic (opus)

## Problem

Current logging uses free-form string concatenation (`self.server.log(f"...")`), making logs difficult to parse, filter, and analyze. No log rotation exists, causing unbounded log file growth.

## Objective

Implement structured logging with:
1. Consistent field-based log format (timestamp, level, operation, user, result)
2. JSON-formatted logs for machine parsing
3. Human-readable console output for development
4. Automatic log rotation by size and time

## Context

**Current approach**:
```python
self.server.log(f"[SECURITY] [BLOCKED] File upload blocked from {nick}@{addr}")
```

**Problems**:
- Inconsistent format across different log calls
- Hard to parse programmatically
- No severity levels (DEBUG, INFO, WARN, ERROR)
- No log rotation - files grow forever
- No structured fields for filtering

## Proposed Solution

Use Python's `logging` module with structured formatters:

```python
import logging
import logging.handlers
from pythonjsonlogger import jsonlogger

# Configure structured logger
logger = logging.getLogger('csc_irc_server')
logger.setLevel(logging.DEBUG)

# Console handler (human-readable)
console_handler = logging.StreamHandler()
console_format = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(operation)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(console_format)

# File handler (JSON, rotated)
file_handler = logging.handlers.RotatingFileHandler(
    'logs/irc_server.json',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
json_format = jsonlogger.JsonFormatter(
    '%(timestamp)s %(level)s %(operation)s %(user)s %(channel)s %(result)s %(message)s'
)
file_handler.setFormatter(json_format)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
```

## Structured Log Fields

Standard fields for all log entries:

- `timestamp` - ISO 8601 timestamp
- `level` - DEBUG, INFO, WARN, ERROR, CRITICAL
- `operation` - Command/operation being performed (JOIN, PRIVMSG, FILE_UPLOAD, etc.)
- `user` - Nick or addr of user involved
- `channel` - Channel name (if applicable)
- `result` - OK, BLOCKED, ERROR, etc.
- `message` - Human-readable description
- `extra` - Dict for additional context

## Example Conversions

**Before**:
```python
self.server.log(f"[SECURITY] [BLOCKED] File upload blocked from {nick}@{addr}")
```

**After**:
```python
logger.warning("File upload blocked", extra={
    'operation': 'FILE_UPLOAD',
    'user': f"{nick}@{addr}",
    'result': 'BLOCKED',
    'reason': 'unauthorized'
})
```

**JSON output**:
```json
{
  "timestamp": "2026-03-13T04:30:15.123Z",
  "level": "WARNING",
  "operation": "FILE_UPLOAD",
  "user": "alice@192.168.1.100",
  "result": "BLOCKED",
  "reason": "unauthorized",
  "message": "File upload blocked"
}
```

**Console output**:
```
2026-03-13 04:30:15 [WARN] FILE_UPLOAD: File upload blocked
```

## Implementation Steps

1. Install python-json-logger:
   ```bash
   pip install python-json-logger
   ```

2. Create `irc/packages/csc-service/csc_service/shared/logging_config.py`:
   - Configure rotating file handler
   - Configure console handler
   - Define standard log fields
   - Export configured logger

3. Update `server.py`:
   - Replace `self.log()` method with structured logger
   - Add `logger` property to server class
   - Migrate existing log calls

4. Update all log calls in:
   - `server_message_handler.py` - IRC command logs
   - `file_handler.py` - File transfer logs
   - `service_handler.py` - Service command logs

5. Create `logs/` directory if it doesn't exist

6. Add log rotation configuration to `etc/settings.json`:
   ```json
   "logging": {
     "level": "INFO",
     "max_bytes": 10485760,
     "backup_count": 5,
     "json_logs": true
   }
   ```

## Acceptance Criteria

- [ ] Structured logger configured with rotation
- [ ] All `self.server.log()` calls converted to structured format
- [ ] JSON logs written to `logs/irc_server.json`
- [ ] Human-readable logs on console
- [ ] Log rotation works (10MB files, 5 backups)
- [ ] Standard fields (timestamp, level, operation, user, result) present
- [ ] Documentation updated with log format spec
- [ ] Example log queries/filters provided

## Files to Create

- `irc/packages/csc-service/csc_service/shared/logging_config.py` - Logger setup

## Files to Modify

- `irc/packages/csc-service/csc_service/server/server.py` - Use structured logger
- `irc/packages/csc-service/csc_service/server/server_message_handler.py` - Convert log calls
- `irc/packages/csc-service/csc_service/server/file_handler.py` - Convert log calls
- `etc/settings.json` - Add logging configuration

## Testing

1. Start server with structured logging
2. Perform various operations (JOIN, PRIVMSG, file upload, etc.)
3. Verify logs appear in both console and JSON file
4. Verify JSON is valid and parseable:
   ```bash
   cat logs/irc_server.json | jq '.'
   ```
5. Test log rotation:
   ```python
   # Generate 15MB of logs, verify rotation happens
   ```
6. Test log filtering:
   ```bash
   # Find all BLOCKED operations
   jq 'select(.result == "BLOCKED")' logs/irc_server.json
   # Find all operations by user "alice"
   jq 'select(.user | contains("alice"))' logs/irc_server.json
   ```

## Notes

- JSON logs enable powerful querying and analysis
- Console logs remain human-friendly for development
- Log rotation prevents disk space issues
- Structured logging is standard practice in production systems
- Consider log aggregation (ELK, Splunk) in future
- Add log level control via environment variable or config
- Performance: JSON formatting is slightly slower but worth it for observability

## Example Log Queries

```bash
# All errors in the last hour
jq 'select(.level == "ERROR")' logs/irc_server.json

# All JOIN operations
jq 'select(.operation == "JOIN")' logs/irc_server.json

# All activity by user "alice"
jq 'select(.user | contains("alice"))' logs/irc_server.json

# All blocked operations
jq 'select(.result == "BLOCKED")' logs/irc_server.json

# Command frequency statistics
jq -r '.operation' logs/irc_server.json | sort | uniq -c | sort -rn
```
