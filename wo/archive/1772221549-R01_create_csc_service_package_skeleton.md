# R01: Create csc-service Package Skeleton

## Depends: None

## Task
Create the empty package directory structure for `csc-service`.

## Steps
1. Create these directories (all empty, each with `__init__.py`):
```
packages/csc-service/
├── csc_service/
│   ├── __init__.py
│   ├── shared/
│   │   ├── __init__.py
│   │   └── services/
│   │       └── __init__.py
│   ├── server/
│   │   └── __init__.py
│   ├── client/
│   │   └── __init__.py
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── claude/
│   │   │   └── __init__.py
│   │   ├── gemini/
│   │   │   └── __init__.py
│   │   └── chatgpt/
│   │       └── __init__.py
│   ├── bridge/
│   │   └── __init__.py
│   └── infra/
│       └── __init__.py
└── pyproject.toml
```

2. Create `packages/csc-service/pyproject.toml`:
```toml
[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "csc-service"
version = "1.0.0"
description = "CSC unified service - IRC server, clients, and infrastructure"
requires-python = ">=3.8"

[project.scripts]
csc-service = "csc_service.main:main"

[tool.setuptools.packages.find]
where = ["."]
include = ["csc_service*"]
```

3. Every `__init__.py` is just an empty file (zero bytes or single newline).

## Verification
- `ls packages/csc-service/csc_service/shared/services/__init__.py` exists
- `ls packages/csc-service/csc_service/infra/__init__.py` exists
- `ls packages/csc-service/pyproject.toml` exists


DEAD END - csc-service package already consolidated and operational
