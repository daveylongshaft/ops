---
agent: haiku
platform: [linux, windows, android]
---

# Create Docker Prompt Templates

## Objective

Create two reusable prompt templates for Docker-based agent tasks: one for Python3, one for Bash.

## Files to Create

- `prompts/TEMPLATE_docker_python3.md`
- `prompts/TEMPLATE_docker_bash.md`

## Template Structure

Both templates must follow this exact section structure:

```markdown
---
agent: coding-agent
model: <python3 or bash>
platform: [linux, windows, android]
---

# [TITLE — Replace with task name]

## Objective

[One paragraph describing what this task accomplishes]

## Requirements

- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

## Code Context

Read these files first:
- `tools/INDEX.txt` — package overview and file map
- `grep <keyword> p-files.list` — find files by name quickly

Relevant packages:
- [List packages this task touches]

## Implementation Steps

1. Step 1
2. Step 2
3. Step 3

## Testing

Write tests for all changes. Place them in `tests/test_<name>.py`.

DO NOT run tests — cron handles test execution. Just write the test files.

Follow existing test patterns in `tests/` for structure and imports.

## Work Log

Journal every step BEFORE doing it:
```bash
echo '<what you are doing and why>' >> prompts/wip/FILENAME.md
```

## Success Criteria

- [ ] All requirements met
- [ ] Test file(s) created in tests/
- [ ] Code committed and pushed
- [ ] This file ends with STATUS: COMPLETE

When all criteria are met, append this exact line as the LAST line of this file:
STATUS: COMPLETE
```

## Python3 Template Specifics (`TEMPLATE_docker_python3.md`)

- Front-matter: `model: python3`
- Add a "Python Guidelines" section after Code Context:
  ```markdown
  ## Python Guidelines

  - Python 3.8+ compatible (no walrus operator in critical paths)
  - Use `pathlib.Path` for all file paths (cross-platform)
  - Use `encoding='utf-8'` for all file I/O
  - Follow existing code style in the package you're modifying
  ```

## Bash Template Specifics (`TEMPLATE_docker_bash.md`)

- Front-matter: `model: bash`
- Add a "Bash Guidelines" section after Code Context:
  ```markdown
  ## Bash Guidelines

  - Use `#!/usr/bin/env bash` shebang
  - Quote all variables: `"$var"` not `$var`
  - Use `set -euo pipefail` at the top of scripts
  - Cross-platform: test on both Linux and MSYS2/Git Bash
  - Use `$(command)` not backticks
  ```

## Work Log

Journal every step to this file using:
```bash
echo '<step>' >> prompts/wip/haiku-create-docker-prompt-templates.md
```

## Success Criteria

- `prompts/TEMPLATE_docker_python3.md` exists with all sections
- `prompts/TEMPLATE_docker_bash.md` exists with all sections
- Both have correct YAML front-matter
- Both include the STATUS: COMPLETE instruction
- Templates are clearly marked as templates (placeholder text, not real tasks)

STATUS: COMPLETE
