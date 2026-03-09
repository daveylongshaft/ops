---
urgency: P2
agent: haiku
requires: python,google-genai
tags: tools,builtin,google-search,code-execution
blockedBy: gemini-api-workflows-00-skeleton.md
---

# Workorder: Gemini Batch API - Built-in Tools (Google Search, Code Execution)

## Context
Wrap Gemini's built-in tools (google_search, code_execution) in a unified interface. These tools are optional, cannot be combined with custom tools on Gemini 3.x, and require special handling in responses.

**Related:** Part 7 of 12-part series. Blocked by workorder 00. Used by workorder 04 (tool-runner).

## Deliverables

### Create `bin/gemini-batch/gbatch_builtin.py`

### 1. `GoogleSearchTool` Class

**`get_tool() -> google.genai.types.Tool`**
- Return Gemini Tool object configured for google_search:
  ```python
  Tool(
      google_search=types.GoogleSearch()
  )
  ```

**`extract_sources(response: google.genai.types.GenerateContentResponse) -> list[dict]`**
- Inspect response for grounding metadata (search chunks)
- Extract: title, URI, snippet from each chunk
- Return list of dicts:
  ```python
  [
    {"title": "...", "uri": "...", "snippet": "..."},
    ...
  ]
  ```
- If no grounding data: return empty list

**`format_citation_block(response: google.genai.types.GenerateContentResponse) -> str`**
- Build markdown citation block from search sources
- Format:
  ```markdown
  ## Sources

  1. [Title](URI)
     Snippet: ...

  2. [Title](URI)
     Snippet: ...
  ```
- If no sources: return empty string

---

### 2. `CodeExecutionTool` Class

**`get_tool() -> google.genai.types.Tool`**
- Return Gemini Tool object configured for code_execution:
  ```python
  Tool(
      code_execution=types.ToolCodeExecution()
  )
  ```

**`extract_results(response: google.genai.types.GenerateContentResponse) -> list[dict]`**
- Inspect response parts for ExecutableCode and CodeExecutionResult
- Extract: code string, execution output, outcome (SUCCESS/ERROR)
- Return list of dicts:
  ```python
  [
    {
      "code": "print('hello')",
      "output": "hello\n",
      "outcome": "SUCCESS"
    },
    ...
  ]
  ```
- If no code execution results: return empty list

**`format_results(response: google.genai.types.GenerateContentResponse) -> str`**
- Build markdown code execution results block
- Format:
  ```markdown
  ## Code Execution Results

  ### Result 1
  ```python
  print('hello')
  ```
  Output:
  ```
  hello
  ```
  Status: SUCCESS

  ### Result 2
  ...
  ```
- If no results: return empty string

---

### 3. `BuiltinToolRegistry` Class

**`__init__(self)`:**
- Initialize tool instances (GoogleSearchTool, CodeExecutionTool)

**`get_tool(name: str) -> google.genai.types.Tool`**
- Dispatch by name: "google_search" → GoogleSearchTool.get_tool(), "code_execution" → CodeExecutionTool.get_tool()
- If unknown: raise ValueError with clear message

**`get_tools(names: list[str]) -> list[google.genai.types.Tool]`**
- For each name: call `get_tool(name)`
- Return list of Tool objects
- If any unknown: raise ValueError with all unknown names listed

**`parse_names(comma_str: str) -> list[str]`**
- Split "code_execution,google_search" into ["code_execution", "google_search"]
- Strip whitespace from each
- Filter empty strings
- Return list of tool names

**`validate_no_conflict(custom_tool_count: int) -> None`**
- If custom_tool_count > 0 and any built-in tools requested:
  - Raise ValueError: `"ERROR: Cannot combine custom tools with built-in tools on Gemini 3.x. This is an API limitation."`
- Called by workorder 04 (tool-runner) before initializing tools

---

## Testing Notes
- Unit test: `test_google_search_tool_extraction()` — mock response with grounding chunks, verify extraction
- Unit test: `test_code_execution_tool_extraction()` — mock response with code results, verify extraction
- Unit test: `test_builtin_tool_registry_get_tool()` — verify correct tool returned by name
- Unit test: `test_builtin_tool_parse_names()` — parse "code_execution,google_search" correctly
- Unit test: `test_builtin_tool_validate_no_conflict()` — verify error when mixing tool types

## Notes
- Built-in tools are Gemini API native (no custom function declarations needed)
- Cannot use built-in tools AND custom function tools in same request on Gemini 3.x
- Response handling differs:
  - Custom tools: `FunctionCall` parts with args, tool loop executes and feeds back results
  - Built-in tools: execution happens server-side, results appear in response parts as grounding/code execution metadata
- GoogleSearchTool response metadata key may be `grounding_chunks`, `search_results`, or similar (verify in Gemini API docs)
- CodeExecutionTool responses include both the code that ran and its output
