> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# R34: Install csc-service and Run Smoke Test

## Depends: R23, R31, R32, R33

## Task
Install csc-service in dev mode and verify basic imports work.

## Steps

1. Uninstall old packages to avoid conflicts:
```bash
pip uninstall -y csc-shared csc-server csc-client csc-claude csc-gemini csc-chatgpt csc-bridge 2>/dev/null
```

2. Install csc-service:
```bash
pip install -e packages/csc-service
```

3. Run import smoke tests:
```bash
python -c "from csc_service.shared.irc import IRCMessage; print('shared OK')"
python -c "from csc_service.server.server import Server; print('server OK')"
python -c "from csc_service.client.client import Client; print('client OK')"
python -c "from csc_service.infra.pm import run_cycle; print('pm OK')"
python -c "from csc_service.infra.git_sync import pull; print('git_sync OK')"
```

4. Test compat shims:
```bash
python -c "from csc_shared.irc import IRCMessage; print('compat shared OK')"
python -c "from csc_server.server import Server; print('compat server OK')"
python -c "from csc_client.client import Client; print('compat client OK')"
```

5. Test console scripts:
```bash
csc-service 2>&1 | head -3
csc-ctl status
```

## If Any Import Fails
- Read the error message carefully
- The most common issue is a missing `__init__.py` — check the directory has one
- Second most common is a typo in the import rewrite (R15-R22)
- Fix the issue in the relevant file and retry

## Verification
- All 8 import tests print "OK"
- `csc-service` prints usage text
- `csc-ctl status` prints component states
