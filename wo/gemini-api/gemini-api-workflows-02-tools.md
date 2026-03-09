---
urgency: P2
agent: sonnet
requires: python,google-genai,safety-review
tags: tools,function-calling,safety
blockedBy: gemini-api-workflows-00-skeleton.md
---

# Workorder: Gemini Batch API - Custom Tool Functions & Executor

## Context
Implement custom tool support for Gemini's function calling API. This module defines file I/O, shell command, and search tools plus a multi-turn loop executor that orchestrates tool calls and result feeding.

**Related:** Part 3 of 12-part series. Unblocks workorders 04, 08.

## Deliverables

### Create `bin/gemini-batch/gbatch_tools.py`

### 1. Tool Function Declarations
Define functions callable by Gemini model via function calling. Each is a Python function that `ToolExecutor` will call.

**`read_file(path: str) -> str`**
- Read file at `path` relative to `/c/csc/`
- Return full contents as string
- Error: file not found → return `"ERROR: File not found: <path>"`

**`write_file(path: str, content: str) -> str`**
- Write/overwrite file at `path` (relative to `/c/csc/`)
- Create parent directories if missing
- Return `"OK: Written N bytes to <path>"`
- Error: permission denied → return `"ERROR: Permission denied: <path>"`

**`list_directory(path: str) -> str`**
- List directory contents at `path` (relative to `/c/csc/`)
- Return newline-separated list of files and subdirs
- Error: not a directory → return `"ERROR: Not a directory: <path>"`

**`run_command(command: str, cwd: str = "/c/csc") -> str`**
- Execute shell command in specified working directory
- Return stdout + stderr combined
- **Safety checks (BLOCK these):**
  - `rm -rf` patterns
  - `git push --force`
  - `git reset --hard`
  - `git rebase` or interactive git operations
  - Path traversal outside `/c/csc/` (e.g., `../../../etc/passwd`)
  - Commands with `;` or `|` redirection to dangerous targets
- On blocked: return `"BLOCKED: <reason>"`
- Timeout: 30 seconds, return `"TIMEOUT: Command did not complete within 30s"`

**`glob_files(pattern: str, base: str = "/c/csc") -> str`**
- Find files matching glob pattern (e.g., `**/*.py`, `bin/**/test*.py`)
- Return newline-separated list of matching paths
- Error: no matches → return `"No matches for pattern: <pattern>"`

**`search_files(pattern: str, path: str = "/c/csc", file_glob: str = "*.py") -> str`**
- Search file contents for regex pattern
- Only search files matching `file_glob` within `path`
- Return lines matching pattern: `<file>:<line_no>:<matched_line>`
- Error: no matches → return `"No matches for pattern: <pattern>"`

### 2. Function Declaration Builder
**`get_tool_declarations() -> list[google.genai.types.FunctionDeclaration]`**

Convert Python functions above into Gemini FunctionDeclaration objects. Each declaration includes:
- Function name (e.g., `read_file`)
- Description (1-2 sentences)
- Parameters: name, type (`string`), description
- Required parameters list

Example:
```python
FunctionDeclaration(
    name="read_file",
    description="Read the full contents of a file from /c/csc directory.",
    parameters=Schema(
        type=SchemaType.OBJECT,
        properties={
            "path": Schema(type=SchemaType.STRING, description="Relative path from /c/csc/")
        },
        required=["path"]
    )
)
```

### 3. `ToolExecutor` Class
Orchestrates multi-turn tool calling with the Gemini API.

**`__init__(self)`:**
- Initialize empty messages list
- Initialize tool declarations

**`get_tool_declarations() -> list[FunctionDeclaration]`:**
- Return all 6 tool declarations (read, write, list, run, glob, search)

**`execute(self, function_call: google.genai.types.FunctionCall) -> str`:**
- Dispatch function call to corresponding Python function
- Call function with args from `function_call.args`
- Return string result
- If unknown function: return `"ERROR: Unknown function: <name>"`

**`run_tool_loop(self, client: google.genai.Client, model: str, system_text: str, prompt: str, max_rounds: int = 20) -> str`:**

Multi-turn loop:
1. Initialize `messages = [{"role": "user", "parts": [{"text": prompt}]}]`
2. For round 1 to max_rounds:
   a. Build request:
      ```python
      response = client.models.generate_content(
          model=model,
          contents=messages,
          tools=[Tool(function_declarations=self.get_tool_declarations())],
          system_instruction=system_text,
          generation_config=GenerationConfig(max_output_tokens=8192, temperature=0)
      )
      ```
   b. Append response to messages
   c. Check `response.candidates[0].content.parts` for `FunctionCall` parts
   d. If no function calls found (only text/content parts):
      - Extract final text answer
      - Log: `"Round <N>: Complete. Final answer: <first 100 chars>..."`
      - Return final text
   e. If function calls found:
      - For each call:
        - Log: `"Round <N>: Calling <function_name>(<args>)"`
        - Execute: `result = self.execute(call)`
        - Append tool result to messages:
          ```python
          {
              "role": "user",
              "parts": [
                  FunctionResponse(name=call.name, response={"result": result})
              ]
          }
          ```
   f. Continue to next round
3. If max_rounds exceeded without final answer: return `"ERROR: Max tool rounds exceeded"`

**Logging:**
- Print each round to stdout (for `agent tail` to capture)
- Format: `"[Round N] Calling <tool>(<args>)"`

### Error Handling
- Timeout in tool call: return `"TIMEOUT: <tool_name> did not complete"`
- Invalid function call: return error, continue loop
- Bad JSON in function args: return error, continue loop

## Testing Notes
- Unit test: `test_tool_executor_read_file()` — mock filesystem, verify read
- Unit test: `test_tool_executor_write_file()` — verify write creates file
- Unit test: `test_tool_executor_run_command_safety()` — verify dangerous commands rejected
- Unit test: `test_tool_loop_termination()` — mock client returning no function calls, verify loop exits

## Notes
- Built-in tools (google_search, code_execution) handled separately in workorder 06
- Custom tools conflict with built-in tools on Gemini 3.x (will validate in workorder 04)
- All paths relative to `/c/csc/`
- Safety is critical: err on the side of blocking uncertain commands
