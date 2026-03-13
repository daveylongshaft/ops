# Add Comprehensive Startup Health Checks

**Priority**: P2 (reliability)
**Estimate**: 3 hours
**Assignee**: jules | codex | gemini
**Reviewer**: anthropic (opus)

## Problem

The IRC server starts without verifying critical preconditions:
- No port conflict detection (fails silently if port in use)
- No JSON validity checks (crashes mid-startup on corrupt files)
- No dependency verification (assumes all Python modules exist)
- No permission checks (file/directory write access)

Result: Server crashes mid-operation or runs in degraded state without clear error messages.

## Objective

Add comprehensive health checks at startup that verify:
1. Port availability (not in use by another process)
2. All config files are valid JSON
3. Required directories exist and are writable
4. Python dependencies are installed
5. File permissions are correct

Server should FAIL FAST with clear errors if checks fail.

## Context

**Current startup flow**:
```python
def main():
    server = IRCServer()
    server.start()  # No precondition checks!
```

**Problems**:
- Port bind failure crashes server
- Corrupt JSON discovered mid-request
- No visibility into missing dependencies
- No "ready for traffic" signal

## Proposed Solution

Add health check module that runs before server start:

```python
class HealthChecker:
    def __init__(self, config):
        self.config = config
        self.checks = [
            self.check_port_available,
            self.check_config_files,
            self.check_directories,
            self.check_dependencies,
            self.check_permissions
        ]

    def run_all_checks(self):
        """Run all health checks. Returns (success, errors)."""
        errors = []
        for check in self.checks:
            try:
                check()
            except HealthCheckError as e:
                errors.append(str(e))

        if errors:
            return False, errors
        return True, []
```

## Health Checks to Implement

### 1. Port Availability Check

```python
def check_port_available(self):
    """Verify server port is not in use."""
    port = self.config.get('port', 9525)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(('0.0.0.0', port))
        sock.close()
    except OSError as e:
        raise HealthCheckError(f"Port {port} is already in use: {e}")
```

**Checks**:
- UDP port is available for binding
- No other server instance running
- Reports process ID if port is in use (on supported platforms)

### 2. Config File Validation

```python
def check_config_files(self):
    """Verify all JSON config files are valid."""
    config_files = [
        'etc/settings.json',
        'etc/platform.json',
        'etc/opers.json',
        'etc/users.json',
        'etc/channels.json',
        'etc/bans.json'
    ]

    for path in config_files:
        if not os.path.exists(path):
            raise HealthCheckError(f"Missing config file: {path}")

        try:
            with open(path) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            raise HealthCheckError(f"Invalid JSON in {path}: {e}")
```

**Checks**:
- All required config files exist
- All config files are valid JSON
- Config files are readable
- Reports line/column of JSON errors

### 3. Directory Verification

```python
def check_directories(self):
    """Verify required directories exist and are writable."""
    required_dirs = [
        'etc/',      # Config files
        'logs/',     # Log output
        'uploads/',  # File uploads
        'tmp/'       # Temporary files
    ]

    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except OSError as e:
                raise HealthCheckError(f"Cannot create directory {dir_path}: {e}")

        # Test write access
        test_file = os.path.join(dir_path, '.write_test')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except OSError as e:
            raise HealthCheckError(f"Directory {dir_path} is not writable: {e}")
```

**Checks**:
- Required directories exist or can be created
- Directories are writable
- Adequate disk space available

### 4. Dependency Verification

```python
def check_dependencies(self):
    """Verify all required Python packages are installed."""
    required = [
        'jsonschema',
        'python-json-logger',
        # Add more as needed
    ]

    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)

    if missing:
        raise HealthCheckError(f"Missing Python packages: {', '.join(missing)}")
```

**Checks**:
- All required pip packages installed
- Correct package versions (if version constraints exist)

### 5. Permission Checks

```python
def check_permissions(self):
    """Verify file permissions for sensitive files."""
    # Check oper config is not world-readable
    if os.path.exists('etc/opers.json'):
        mode = os.stat('etc/opers.json').st_mode
        if mode & 0o004:  # World-readable
            logger.warning("etc/opers.json is world-readable (security risk)")
```

**Checks**:
- Sensitive files not world-readable
- Server has permission to bind privileged ports (if needed)

## Implementation Steps

1. Create `irc/packages/csc-service/csc_service/server/health_check.py`:
   - Define `HealthCheckError` exception
   - Implement `HealthChecker` class
   - Implement all 5 check methods

2. Update `server/main.py`:
   ```python
   def main():
       # Load config
       config = load_config('etc/settings.json')

       # Run health checks
       checker = HealthChecker(config)
       success, errors = checker.run_all_checks()

       if not success:
           logger.error("Health check failed:")
           for error in errors:
               logger.error(f"  - {error}")
           sys.exit(1)

       logger.info("All health checks passed")

       # Start server
       server = IRCServer(config)
       server.start()
   ```

3. Add health check endpoint:
   ```python
   # IRC command: /ADMIN HEALTHCHECK
   # Returns JSON with check results
   ```

4. Add startup banner with check summary:
   ```
   ==========================================
   CSC IRC Server v1.0
   ==========================================
   [OK] Port 9525 available
   [OK] Config files valid
   [OK] Directories writable
   [OK] Dependencies installed
   [OK] Permissions correct

   Server ready on port 9525
   ==========================================
   ```

## Acceptance Criteria

- [ ] All 5 health check categories implemented
- [ ] Server exits with error code 1 on failed check
- [ ] Clear error messages for each failure type
- [ ] Health checks complete in <1 second
- [ ] Startup banner shows check results
- [ ] Health check endpoint available via IRC command
- [ ] Documentation for troubleshooting failed checks

## Files to Create

- `irc/packages/csc-service/csc_service/server/health_check.py` - Health checker

## Files to Modify

- `irc/packages/csc-service/csc_service/server/main.py` - Run checks on startup
- `irc/packages/csc-service/csc_service/server/server_message_handler.py` - Add HEALTHCHECK command

## Testing

1. **Port conflict test**:
   ```bash
   # Start server on port 9525
   # Try to start second instance
   # Verify: Clear error "Port 9525 already in use"
   ```

2. **Corrupt JSON test**:
   ```bash
   echo "{ invalid" > etc/settings.json
   # Verify: Error with file name and line number
   ```

3. **Missing directory test**:
   ```bash
   rm -rf logs/
   # Verify: Directory auto-created with write test
   ```

4. **Missing dependency test**:
   ```bash
   pip uninstall jsonschema
   # Verify: Error "Missing Python packages: jsonschema"
   ```

5. **Permission test**:
   ```bash
   chmod 444 etc/opers.json
   # Verify: Warning about world-readable file
   ```

## Notes

- Health checks should be fast (<1s total)
- Fail fast - don't start degraded
- Clear error messages > obscure stack traces
- Consider adding `--skip-health-checks` flag for emergency recovery
- Health checks can run periodically (not just startup)
- Future: Add metrics endpoint (Prometheus-compatible)

## Example Error Output

```
==========================================
CSC IRC Server v1.0 - Startup Failed
==========================================
[FAIL] Port 9525 is already in use
       Another process is bound to this port.
       Process ID: 12345 (if available)
       Solution: Stop the other server or change port in etc/settings.json

[FAIL] Invalid JSON in etc/opers.json
       Expecting ',' delimiter: line 5 column 12 (char 89)
       Solution: Fix JSON syntax or restore from backup

[WARN] Directory logs/ does not exist
       Created automatically

Server startup aborted. Fix errors above and restart.
==========================================
```


--- Agent Log ---
[run_agent] Agent: gemini-2.5-pro, Root: C:\csc, WIP: improve_startup_health_checks.md
[run_agent] Git pull to get work files...
[run_agent] Git pull complete
[run_agent] Starting Gemini (gemini-2.5-pro) for gemini-2.5-pro
YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
YOLO mode is enabled. All tool calls will be automatically approved.
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
Error when talking to Gemini API Full report available at: C:\Users\davey\AppData\Local\Temp\gemini-client-error-Turn.run-sendMessageStream-2026-03-13T11-24-04-085Z.json TerminalQuotaError: You have exhausted your capacity on this model. Your quota will reset after 20h55m19s.
    at classifyGoogleError (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/googleQuotaErrors.js:238:28)
    at retryWithBackoff (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/retry.js:153:37)
    at process.processTicksAndRejections (node:internal/process/task_queues:103:5)
    at async GeminiChat.makeApiCallAndProcessStream (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:445:32)
    at async GeminiChat.streamWithRetries (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:265:40)
    at async Turn.run (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/turn.js:70:30)
    at async GeminiClient.processTurn (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/client.js:478:26)
    at async GeminiClient.sendMessageStream (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/client.js:579:20)
    at async file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/dist/src/nonInteractiveCli.js:194:34
    at async main (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/dist/src/gemini.js:531:9) {
  cause: {
    code: 429,
    message: 'You have exhausted your capacity on this model. Your quota will reset after 20h55m19s.',
    details: [ [Object], [Object] ]
  },
  retryDelayMs: 75319921.240801,
  reason: 'QUOTA_EXHAUSTED'
}
An unexpected critical error occurred:[object Object]
[2026-03-13 06:24:04] [queue-worker] [INFO] ==================================================
[2026-03-13 06:24:04] [queue-worker] [INFO] Cycle start
[2026-03-13 06:24:04] [queue-worker] [INFO] git pull
Store data successful. Saved 1 items to 'C:\Users\davey\AppData\Local\Temp\csc\run\queue_worker_data.json'.
[2026-03-13 06:24:05] [queue-worker] [INFO] Scanned 0 pending workorders from all agents
[2026-03-13 06:24:05] [queue-worker] [INFO] Cycle end (idle)

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)


--- Agent Log ---
[run_agent] Agent: gemini-2.5-pro, Root: C:\csc, WIP: improve_startup_health_checks.md
[run_agent] Git pull to get work files...
[run_agent] Git pull complete
[run_agent] Starting Gemini (gemini-2.5-pro) for gemini-2.5-pro
YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
YOLO mode is enabled. All tool calls will be automatically approved.
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
Error when talking to Gemini API Full report available at: C:\Users\davey\AppData\Local\Temp\gemini-client-error-Turn.run-sendMessageStream-2026-03-13T11-24-40-833Z.json TerminalQuotaError: You have exhausted your capacity on this model. Your quota will reset after 20h54m43s.
    at classifyGoogleError (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/googleQuotaErrors.js:238:28)
    at retryWithBackoff (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/retry.js:153:37)
    at process.processTicksAndRejections (node:internal/process/task_queues:103:5)
    at async GeminiChat.makeApiCallAndProcessStream (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:445:32)
    at async GeminiChat.streamWithRetries (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:265:40)
    at async Turn.run (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/turn.js:70:30)
    at async GeminiClient.processTurn (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/client.js:478:26)
    at async GeminiClient.sendMessageStream (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/client.js:579:20)
    at async file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/dist/src/nonInteractiveCli.js:194:34
    at async main (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/dist/src/gemini.js:531:9) {
  cause: {
    code: 429,
    message: 'You have exhausted your capacity on this model. Your quota will reset after 20h54m43s.',
    details: [ [Object], [Object] ]
  },
  retryDelayMs: 75283144.736773,
  reason: 'QUOTA_EXHAUSTED'
}
An unexpected critical error occurred:[object Object]
[2026-03-13 06:24:41] [queue-worker] [INFO] ==================================================
[2026-03-13 06:24:41] [queue-worker] [INFO] Cycle start
[2026-03-13 06:24:41] [queue-worker] [INFO] git pull
Store data successful. Saved 1 items to 'C:\Users\davey\AppData\Local\Temp\csc\run\queue_worker_data.json'.
[2026-03-13 06:24:42] [queue-worker] [INFO] Scanned 0 pending workorders from all agents
[2026-03-13 06:24:42] [queue-worker] [INFO] Cycle end (idle)

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)


--- Agent Log ---
[run_agent] Agent: sonnet, Root: C:\csc, WIP: improve_startup_health_checks.md
[run_agent] Git pull to get work files...
[run_agent] Git pull complete
[run_agent] Anthropic API (claude-sonnet-4-5-20250929) for sonnet
[run_agent] System prompt: 1,038 chars (cached)
[run_agent] User prompt: 531 chars
[run_agent] Tools: 6 defined, max 100 turns, max_tokens=32768

[run_agent] Fatal API error on turn 0: AuthenticationError: Error code: 401 - {'type': 'error', 'error': {'type': 'authentication_error', 'message': 'invalid x-api-key'}, 'request_id': 'req_011CYzziV1JxVtrPTa6CYGWq'}
[2026-03-13 06:24:54] [queue-worker] [INFO] ==================================================
[2026-03-13 06:24:54] [queue-worker] [INFO] Cycle start
[2026-03-13 06:24:54] [queue-worker] [INFO] git pull
Store data successful. Saved 1 items to 'C:\Users\davey\AppData\Local\Temp\csc\run\queue_worker_data.json'.
[2026-03-13 06:24:55] [queue-worker] [INFO] Scanned 0 pending workorders from all agents
[2026-03-13 06:24:55] [queue-worker] [INFO] Cycle end (idle)

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)
