> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# R28: Create Install/Uninstall Scripts for csc-service

## Depends: R27

## Task
Create convenience scripts to build and run csc-service in Docker.

## Steps

1. Create `bin/install-csc-service.bat` (Windows):
```batch
@echo off
echo Building csc-service Docker image...
docker compose build csc-service
echo Starting csc-service...
docker compose up -d csc-service
echo.
echo csc-service is running. Check logs with:
echo   docker compose logs -f csc-service
```

2. Create `bin/uninstall-csc-service.bat` (Windows):
```batch
@echo off
echo Stopping csc-service...
docker compose down
echo Done.
```

3. Create `bin/install-csc-service.sh` (Linux/macOS):
```bash
#!/bin/bash
set -e
echo "Building csc-service Docker image..."
docker compose build csc-service
echo "Starting csc-service..."
docker compose up -d csc-service
echo ""
echo "csc-service is running. Check logs with:"
echo "  docker compose logs -f csc-service"
```

4. Make the shell script executable:
```bash
chmod +x bin/install-csc-service.sh
```

## Verification
- `cat bin/install-csc-service.bat` exists
- `cat bin/uninstall-csc-service.bat` exists
- `cat bin/install-csc-service.sh` exists
