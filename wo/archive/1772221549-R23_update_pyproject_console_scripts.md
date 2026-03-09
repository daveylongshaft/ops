# R23: Update pyproject.toml with All Console Scripts

## Depends: R14, R17, R18, R19, R20, R21, R22

## Task
Update `packages/csc-service/pyproject.toml` to include all console_scripts
entry points so every component is launchable.

## Steps
Edit `packages/csc-service/pyproject.toml` and set the `[project.scripts]` section to:

```toml
[project.scripts]
csc-service = "csc_service.main:main"
csc-server = "csc_service.server.main:main"
csc-client = "csc_service.client.main:main"
csc-claude = "csc_service.clients.claude.main:main"
csc-gemini = "csc_service.clients.gemini.main:main"
csc-chatgpt = "csc_service.clients.chatgpt.main:main"
csc-bridge = "csc_service.bridge.main:main"
csc-ctl = "csc_service.ctl:main"
```

Also add dependencies:
```toml
[project.optional-dependencies]
claude = ["anthropic"]
gemini = ["google-generativeai"]
chatgpt = ["openai"]
all = ["anthropic", "google-generativeai", "openai"]
```

## Verification
- `pip install -e packages/csc-service`
- `csc-service` prints usage
- `which csc-server` points to the new package (not old one)


DEAD END - csc-service package already consolidated and operational
