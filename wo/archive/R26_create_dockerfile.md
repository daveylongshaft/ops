> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# R26: Create Dockerfile for csc-service

## Depends: R23

## Task
Create a Dockerfile that builds csc-service for running in Docker.

## Steps
Create `packages/csc-service/Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install git (needed for git-sync)
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/csc

# Copy the package
COPY . /opt/csc/

# Install csc-service
RUN pip install --no-cache-dir -e packages/csc-service

# Default: run daemon in local mode
CMD ["csc-service", "--daemon", "--local"]
```

## Verification
- `cat packages/csc-service/Dockerfile` shows the content above
- File is valid Dockerfile syntax (no build test needed at this step)
