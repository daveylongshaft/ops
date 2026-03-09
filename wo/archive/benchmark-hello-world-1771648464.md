# Benchmark: Haiku Model - Simple "Hello World" Multi-Language

This benchmark tests Claude Haiku against the same task as local ollama models.

## Task

Generate working "Hello World" programs in each language:
1. C++ (console output)
2. JavaScript (browser popup - NO msgbox/alert, use actual window)
3. Perl
4. Python
5. Tcl
6. Visual Basic (ASP/classic)
7. PHP
8. Bash

For each language:
- Write complete, runnable code
- Add a comment with timestamp
- Test if syntax is correct
- Note any issues or assumptions

## Output Format

For each language create:
```
## [Language Name]
### Code
[complete code here]

### Notes
- Runtime/issues
- Quality score (1-10)
```

## Acceptance

All 8 languages have working code that can be executed.
Code quality and correctness is rated (1-10).

## Work Log

Executing Haiku benchmark for hello world multi-language test...
PID: 21628 agent: ollama-deepseek starting at 2026-02-20 22:34:25
