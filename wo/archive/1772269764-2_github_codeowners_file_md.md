# Create .github/CODEOWNERS File

## Objective
Create `.github/CODEOWNERS` file that lists all protected paths requiring AI review before merging to main.

## Protected Paths

### Infrastructure Code (PROTECTED)
```
# Critical infrastructure - requires AI review
/packages/csc-service/csc_service/infra/   @ai-reviewer
/packages/csc-service/csc_service/server/  @ai-reviewer
/packages/csc-service/csc_service/shared/  @ai-reviewer
/packages/csc-service/csc_service/cli/     @ai-reviewer

# Scripts - requires AI review
/bin/                                       @ai-reviewer

# Configuration files - requires AI review
*.json                                      @ai-reviewer
*.yaml                                      @ai-reviewer
*.yml                                       @ai-reviewer
```

### Unprotected Paths (Direct Push Allowed)
These paths intentionally NOT in CODEOWNERS so they don't require review:
- `agents/` - Queue management (orders.md, logs)
- `workorders/` - Workorder lifecycle (ready/wip/done/hold/archive)
- `staging_uploads/` - Temporary service upload area
- `services/` - Dynamic service modules

## Implementation
- Create `.github/CODEOWNERS` file at repository root
- Use `@ai-reviewer` as the reviewer account (GitHub bot)
- Comment explaining each section
- Format: one path per line, tab-separated from reviewer handle

## Testing
- Verify GitHub recognizes the file (Settings → Code owners)
- Test: PR touching `packages/csc-service/` shows code owner requirement
- Test: PR touching only `agents/` shows no code owner requirement
- Verify AI reviewer bot is linked correctly
