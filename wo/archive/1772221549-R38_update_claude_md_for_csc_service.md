# R38: Update CLAUDE.md for csc-service

## Depends: R34

## Task
Update the project's CLAUDE.md to document the new csc-service package alongside
the existing packages. Don't remove old package docs yet (they still exist).

## Steps

1. Open `CLAUDE.md`

2. In the "Setup & Installation" section, add after the existing pip install block:
```bash
# New unified package (replaces individual packages)
pip install -e packages/csc-service
# Or with AI client dependencies:
pip install -e "packages/csc-service[all]"
```

3. In the "Running the System" section, add:
```bash
# Unified service (runs test-runner + queue-worker + PM in one process)
csc-service --daemon --local

# Manage components
csc-ctl status
csc-ctl enable claude
csc-ctl set poll_interval 30

# Docker deployment
docker compose up -d csc-service
```

4. In the "File Locations" table, add:
```
| packages/csc-service/ | Unified package (server, clients, infra, bridge) |
```

## Verification
- `grep "csc-service" CLAUDE.md` finds the new sections
- Existing old-package documentation is NOT removed


DEAD END - csc-service package already consolidated and operational
