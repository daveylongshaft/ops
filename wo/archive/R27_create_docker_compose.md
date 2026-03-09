> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# R27: Create docker-compose.yml for csc-service

## Depends: R26

## Task
Create a docker-compose.yml at the project root for easy Docker deployment.

## Steps
Create `docker-compose.yml` in the project root:

```yaml
version: "3.8"

services:
  csc-service:
    build:
      context: .
      dockerfile: packages/csc-service/Dockerfile
    container_name: csc-service
    restart: unless-stopped
    volumes:
      - .:/opt/csc
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY:-}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
    command: ["csc-service", "--daemon", "--local"]
```

## Verification
- `cat docker-compose.yml` shows valid YAML
- Structure defines one service named `csc-service`
