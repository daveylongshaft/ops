#!/usr/bin/env python3
"""
Universal agent runner — detects agent type from directory name and
invokes the correct AI CLI or API.

For Anthropic agents (haiku/sonnet/opus/claude/claude-batch), calls the
Anthropic Messages API directly with tool definitions and prompt caching.
Other agents (Gemini, Ollama) continue to use their respective CLIs.

Usage: run_agent.py <path-to-orders.md>

The agent name is derived from the grandparent directory:
    agents/<agent-name>/bin/run_agent.py
              ↑ this becomes the agent name

Cross-platform: works on Windows, Linux, macOS, Android/Termux.
"""
import glob as globmod
import json
import os
import re
import sys
import shutil
import subprocess
import time
from pathlib import Path


# ---------------------------------------------------------------------------
# Agent → model mapping
# ---------------------------------------------------------------------------

# Anthropic agents: use Anthropic Messages API with tools + prompt caching
ANTHROPIC_AGENTS = {
    "haiku":        "claude-haiku-4-5-20251001",
    "sonnet":       "claude-sonnet-4-5-20250929",
    "opus":         "claude-opus-4-6",
    "claude":       "claude-sonnet-4-5-20250929",
    "claude-batch": "claude-haiku-4-5-20251001",
}

# Legacy alias — code that checks `agent_name in CLAUDE_AGENTS` still works
CLAUDE_AGENTS = ANTHROPIC_AGENTS

# Gemini models: use Gemini CLI
GEMINI_AGENTS = {
    "gemini-3-pro":            "gemini-2.5-pro",
    "gemini-3-flash":          "gemini-2.5-flash",
    "gemini-3-flash-preview":  "gemini-2.5-flash",
    "gemini-2.5-pro":         "gemini-2.5-pro",
    "gemini-2.5-flash":       "gemini-2.5-flash",
    "gemini-2.5-flash-lite":  "gemini-2.5-flash",
    "gemini":                  "gemini-2.5-flash",
}

# Local models via Docker Model Runner / Ollama
LOCAL_AGENTS = {
    "ollama-codellama": "codellama",
    "ollama-deepseek":  "deepseek-coder",
    "ollama-qwen":      "qwen2.5-coder",
    "codellama":        "codellama",
    "deepseek":         "deepseek-coder",
    "qwen":             "qwen2.5-coder",
}


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_TURNS = 100   # Max agentic loop iterations before forced stop
OUTPUT_CAP = 50000  # Max chars returned per tool result

# Scale max_tokens by model capability
MAX_TOKENS_BY_MODEL = {
    "claude-opus-4-6":            32768,
    "claude-sonnet-4-5-20250929": 32768,
    "claude-haiku-4-5-20251001":  8192,
}
DEFAULT_MAX_TOKENS = 16384

# Directories to skip in grep_search
SKIP_DIRS = {".git", "node_modules", ".trash", "__pycache__", ".venv", "venv", ".tox"}


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def detect_agent_name(workorder_path: Path) -> str:
    """Derive agent name from directory structure or environment.

    Priority:
    1. CSC_AGENT_NAME env var (set by queue-worker, most reliable)
    2. Workorder path: agents/<name>/queue/work/orders.md
    3. Script location: agents/<name>/bin/run_agent.py
    4. Fallback: "haiku"
    """
    # Prefer explicit environment variable (set by queue-worker spawn_agent)
    env_name = os.environ.get("CSC_AGENT_NAME", "")
    if env_name:
        return env_name

    # Try from workorder path: agents/<name>/queue/work/orders.md
    parts = workorder_path.resolve().parts
    for i, part in enumerate(parts):
        if part == "agents" and i + 1 < len(parts):
            return parts[i + 1]

    # Try from script location: agents/<name>/bin/run_agent.py
    script_path = Path(__file__).resolve()
    parts = script_path.parts
    for i, part in enumerate(parts):
        if part == "agents" and i + 1 < len(parts):
            return parts[i + 1]

    return "haiku"


def find_csc_root(workorder_path: Path) -> Path:
    """Walk up from workorder to find project root (has CLAUDE.md)."""
    p = workorder_path.resolve().parent
    for _ in range(10):
        if (p / "CLAUDE.md").exists():
            return p
        p = p.parent
    # Fallback: try from script location
    p = Path(__file__).resolve().parent
    for _ in range(10):
        if (p / "CLAUDE.md").exists():
            return p
        p = p.parent
    return Path.cwd()


def _make_env(**extras):
    """Create a clean subprocess environment with UTF-8 encoding."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # Force UTF-8 for Node.js / npx child processes too
    env["LANG"] = env.get("LANG", "en_US.UTF-8")
    env["PYTHONUTF8"] = "1"
    for k, v in extras.items():
        if v is None:
            env.pop(k, None)
        else:
            env[k] = v
    return env


# ---------------------------------------------------------------------------
# Anthropic Messages API runner (replaces Claude CLI for Anthropic agents)
# ---------------------------------------------------------------------------

CLAUDE_SYSTEM_PROMPT = """You are an AI coding agent working on the CSC project. Your working directory is the project root.

## SETUP (do this first)
1. Read your task file (path provided in user message)
2. Read README.1shot for full workflow procedures
3. Read tools/INDEX.txt for the code map
4. Skim tree.txt for directory structure

## JOURNALING (MANDATORY)
Use `python bin/next_step` to journal progress. This is NOT optional.

FIRST: python bin/next_step <wip_file> START
EACH STEP: python bin/next_step <wip_file> "what you're about to do"
WHEN DONE: python bin/next_step <wip_file> COMPLETE

Without journaling, queue-worker cannot detect completion and work is retried.

## RULES
- Journal EVERY step with `python bin/next_step` BEFORE doing it
- Write tests that verify your changes (don't run them)
- Update docs for features you changed
- Do NOT run tests (test-runner handles that)
- Do NOT touch git (queue-worker handles commits/push)
- Do NOT move files between workorders directories
- When complete, ensure the LAST journaled line is COMPLETE
"""


def build_tools():
    """Define the 6 tools available to Anthropic agents, matching Claude Code."""
    return [
        {
            "name": "read_file",
            "description": "Read a file's contents. Returns the text content of the file.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to project root"
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Start line number (1-indexed). Optional."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of lines to read. Optional."
                    },
                },
                "required": ["path"]
            }
        },
        {
            "name": "write_file",
            "description": "Create or overwrite a file with the given content.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to project root"
                    },
                    "content": {
                        "type": "string",
                        "description": "The full content to write to the file"
                    },
                },
                "required": ["path", "content"]
            }
        },
        {
            "name": "edit_file",
            "description": "Replace the first occurrence of old_string with new_string in a file. "
                           "Provide enough context in old_string to make the match unique.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to project root"
                    },
                    "old_string": {
                        "type": "string",
                        "description": "The exact text to find and replace"
                    },
                    "new_string": {
                        "type": "string",
                        "description": "The replacement text"
                    },
                },
                "required": ["path", "old_string", "new_string"]
            }
        },
        {
            "name": "bash",
            "description": "Execute a shell command and return stdout+stderr. "
                           "Use for git-status, running scripts, installing packages, etc.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default 120)"
                    },
                },
                "required": ["command"]
            }
        },
        {
            "name": "glob_files",
            "description": "Find files matching a glob pattern (e.g. '**/*.py', 'tests/*.py'). "
                           "Returns matching file paths, one per line.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern (supports ** for recursive)"
                    },
                },
                "required": ["pattern"]
            }
        },
        {
            "name": "grep_search",
            "description": "Search file contents for a regex pattern. Returns matching lines "
                           "with file paths and line numbers.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Regex pattern to search for"
                    },
                    "path": {
                        "type": "string",
                        "description": "File or directory to search in (default: '.')"
                    },
                    "include": {
                        "type": "string",
                        "description": "Glob filter for filenames (e.g. '*.py')"
                    },
                },
                "required": ["pattern"]
            }
        },
    ]


def _safe_path(csc_root: Path, relative: str) -> Path:
    """Resolve a relative path within csc_root, preventing directory traversal."""
    resolved = (csc_root / relative).resolve()
    root_resolved = csc_root.resolve()
    # Allow paths within the project root
    try:
        resolved.relative_to(root_resolved)
    except ValueError:
        raise ValueError(f"Path escapes project root: {relative}")
    return resolved


def execute_tool(name: str, tool_input: dict, csc_root: Path) -> str:
    """Execute a tool call locally, return result string."""
    try:
        if name == "read_file":
            path = _safe_path(csc_root, tool_input["path"])
            if not path.exists():
                return f"Error: File not found: {tool_input['path']}"
            text = path.read_text(encoding="utf-8", errors="replace")
            lines = text.splitlines(keepends=True)
            offset = tool_input.get("offset", 1) - 1  # Convert to 0-indexed
            if offset < 0:
                offset = 0
            limit = tool_input.get("limit")
            if limit:
                lines = lines[offset:offset + limit]
            else:
                lines = lines[offset:]
            # Add line numbers like cat -n
            numbered = []
            for i, line in enumerate(lines, start=offset + 1):
                numbered.append(f"{i:6d}\t{line}")
            return "".join(numbered)[:OUTPUT_CAP]

        elif name == "write_file":
            path = _safe_path(csc_root, tool_input["path"])
            path.parent.mkdir(parents=True, exist_ok=True)
            content = tool_input["content"]
            path.write_text(content, encoding="utf-8")
            return f"Written {len(content)} bytes to {tool_input['path']}"

        elif name == "edit_file":
            path = _safe_path(csc_root, tool_input["path"])
            if not path.exists():
                return f"Error: File not found: {tool_input['path']}"
            content = path.read_text(encoding="utf-8", errors="replace")
            old = tool_input["old_string"]
            new = tool_input["new_string"]
            if old not in content:
                return f"Error: old_string not found in {tool_input['path']}"
            count = content.count(old)
            if count > 1:
                return (f"Error: old_string found {count} times in {tool_input['path']}. "
                        "Provide more context to make it unique.")
            content = content.replace(old, new, 1)
            path.write_text(content, encoding="utf-8")
            return f"Edited {tool_input['path']}"

        elif name == "bash":
            timeout = tool_input.get("timeout", 120)
            result = subprocess.run(
                tool_input["command"],
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(csc_root),
                timeout=timeout,
            )
            output = result.stdout + result.stderr
            if result.returncode != 0:
                output += f"\n[exit code: {result.returncode}]"
            return output[:OUTPUT_CAP]

        elif name == "glob_files":
            pattern = tool_input["pattern"]
            # Use chdir for Python 3.8 compatibility (root_dir requires 3.10+)
            old_cwd = os.getcwd()
            try:
                os.chdir(str(csc_root))
                matches = globmod.glob(pattern, recursive=True)
            finally:
                os.chdir(old_cwd)
            matches.sort()
            if not matches:
                return f"No files matching: {pattern}"
            return "\n".join(matches[:500])

        elif name == "grep_search":
            pattern = tool_input["pattern"]
            search_path = tool_input.get("path", ".")
            include = tool_input.get("include")
            # Use Python re for portable grep
            target = _safe_path(csc_root, search_path)
            results = []
            try:
                regex = re.compile(pattern)
            except re.error as e:
                return f"Error: Invalid regex: {e}"
            if target.is_file():
                files = [target]
            else:
                glob_pat = include or "**/*"
                files = sorted(target.glob(glob_pat))
            for fpath in files:
                if not fpath.is_file():
                    continue
                # Skip common non-source directories
                if any(part in SKIP_DIRS for part in fpath.parts):
                    continue
                # Skip binary files and large files
                if fpath.stat().st_size > 2_000_000:
                    continue
                try:
                    text = fpath.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                for lineno, line in enumerate(text.splitlines(), 1):
                    if regex.search(line):
                        rel = fpath.relative_to(csc_root)
                        results.append(f"{rel}:{lineno}: {line}")
                        if len(results) >= 200:
                            results.append("... (truncated at 200 matches)")
                            return "\n".join(results)[:OUTPUT_CAP]
            if not results:
                return f"No matches for: {pattern}"
            return "\n".join(results)[:OUTPUT_CAP]

        else:
            return f"Error: Unknown tool: {name}"

    except ValueError as e:
        return f"Error: {e}"
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {tool_input.get('timeout', 120)}s"
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"


def build_cached_system_prompt(csc_root: Path):
    """Build system prompt from project context files with cache_control."""
    parts = [CLAUDE_SYSTEM_PROMPT]

    # Add CLAUDE.md for full project context
    claude_md = csc_root / "CLAUDE.md"
    if claude_md.exists():
        try:
            parts.append(f"\n\n## Project Reference (CLAUDE.md)\n\n{claude_md.read_text(encoding='utf-8', errors='replace')}")
        except Exception:
            pass

    # Add code maps for navigation
    index = csc_root / "tools" / "INDEX.txt"
    if index.exists():
        try:
            parts.append(f"\n\n## Code Maps (tools/INDEX.txt)\n\n{index.read_text(encoding='utf-8', errors='replace')}")
        except Exception:
            pass

    combined = "\n".join(parts)
    return [
        {
            "type": "text",
            "text": combined,
            "cache_control": {"type": "ephemeral"}  # 5-min TTL, ~90% savings on hits
        }
    ]


def log_usage(turn: int, usage):
    """Log token usage for a single turn, including cache stats."""
    input_tok = getattr(usage, "input_tokens", 0)
    output_tok = getattr(usage, "output_tokens", 0)
    cache_create = getattr(usage, "cache_creation_input_tokens", 0)
    cache_read = getattr(usage, "cache_read_input_tokens", 0)

    parts = [f"[turn {turn:3d}] in={input_tok:,} out={output_tok:,}"]
    if cache_create:
        parts.append(f"cache_write={cache_create:,}")
    if cache_read:
        parts.append(f"cache_read={cache_read:,}")
    print(" ".join(parts))
    sys.stdout.flush()


def run_anthropic_api(agent_name: str, model: str, user_prompt: str, csc_root: Path):
    """Run workorder via Anthropic Messages API with tools + prompt caching.

    Uses streaming to prevent HTTP timeouts on large inputs.
    Implements a manual agentic loop: API call → tool execution → repeat.
    """
    try:
        from anthropic import Anthropic, RateLimitError, APIConnectionError, InternalServerError
    except ImportError:
        print("[run_agent] ERROR: anthropic package not installed (pip install anthropic)")
        print("[run_agent] Falling back to Claude CLI...")
        return run_claude_cli(agent_name, model, user_prompt, csc_root)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[run_agent] ERROR: ANTHROPIC_API_KEY not set")
        print("[run_agent] Falling back to Claude CLI...")
        return run_claude_cli(agent_name, model, user_prompt, csc_root)

    client = Anthropic()
    tools = build_tools()
    system = build_cached_system_prompt(csc_root)
    messages = [{"role": "user", "content": user_prompt}]

    sys_chars = sum(len(b["text"]) for b in system)
    print(f"[run_agent] Anthropic API ({model}) for {agent_name}")
    print(f"[run_agent] System prompt: {sys_chars:,} chars (cached)")
    print(f"[run_agent] User prompt: {len(user_prompt):,} chars")
    max_tokens = MAX_TOKENS_BY_MODEL.get(model, DEFAULT_MAX_TOKENS)
    print(f"[run_agent] Tools: {len(tools)} defined, max {MAX_TURNS} turns, max_tokens={max_tokens}")
    sys.stdout.flush()

    total_input = 0
    total_output = 0
    total_cache_read = 0
    retry_count = 0

    for turn in range(MAX_TURNS):
        try:
            # Use streaming to prevent HTTP timeouts with large context
            with client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                system=system,
                tools=tools,
                messages=messages,
            ) as stream:
                # Print text output live for monitoring
                for text in stream.text_stream:
                    print(text, end="", flush=True)
                response = stream.get_final_message()
            retry_count = 0  # Reset on success
        except (RateLimitError, APIConnectionError, InternalServerError) as e:
            retry_count += 1
            wait = min(60, 2 ** min(retry_count, 6))
            print(f"\n[run_agent] Retryable error (attempt {retry_count}), waiting {wait}s: {e}")
            time.sleep(wait)
            if retry_count >= 5:
                print(f"[run_agent] Too many retries ({retry_count}), giving up")
                return 1
            continue
        except Exception as e:
            print(f"\n[run_agent] Fatal API error on turn {turn}: {type(e).__name__}: {e}")
            return 1

        # Track usage
        usage = response.usage
        input_tok = getattr(usage, "input_tokens", 0)
        output_tok = getattr(usage, "output_tokens", 0)
        cache_read = getattr(usage, "cache_read_input_tokens", 0)
        total_input += input_tok
        total_output += output_tok
        total_cache_read += cache_read

        log_usage(turn, usage)

        # Append assistant response to conversation
        messages.append({"role": "assistant", "content": response.content})

        # Check stop reason
        if response.stop_reason == "end_turn":
            print(f"\n[run_agent] Completed after {turn + 1} turns")
            break

        if response.stop_reason == "max_tokens":
            print(f"\n[run_agent] WARNING: Hit max_tokens on turn {turn}")
            # Check if response ends with a partial tool_use block
            has_partial_tool = any(
                block.type == "tool_use" for block in response.content
            )
            if has_partial_tool:
                # Tool calls were truncated — ask model to retry without the partial call
                # Drop the truncated assistant message and prompt a fresh attempt
                print("[run_agent] Partial tool_use detected in truncated response, retrying turn")
                messages.append({"role": "user", "content": (
                    "Your previous response was truncated mid-tool-call. "
                    "Please try again, breaking your work into smaller steps."
                )})
            else:
                messages.append({"role": "user", "content": "Continue from where you left off."})
            continue

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"\n[tool] {block.name}({json.dumps(block.input, ensure_ascii=False)[:200]})")
                    sys.stdout.flush()
                    result = execute_tool(block.name, block.input, csc_root)
                    # Show truncated result for monitoring
                    preview = result[:200].replace("\n", " ")
                    print(f"  → {preview}{'...' if len(result) > 200 else ''}")
                    sys.stdout.flush()
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)[:OUTPUT_CAP],
                    })
            messages.append({"role": "user", "content": tool_results})
            continue

        # Unknown stop reason
        print(f"\n[run_agent] Unexpected stop_reason: {response.stop_reason}")
        break

    else:
        print(f"\n[run_agent] WARNING: Hit MAX_TURNS ({MAX_TURNS})")

    # Summary
    print(f"\n[run_agent] Token totals: input={total_input:,} output={total_output:,} cache_read={total_cache_read:,}")
    sys.stdout.flush()
    return 0


# ---------------------------------------------------------------------------
# CLI-based runners (fallback for Anthropic, primary for Gemini/local)
# ---------------------------------------------------------------------------

def run_claude_cli(agent_name: str, model: str, user_prompt: str, csc_root: Path):
    """Invoke Claude Code CLI with system prompt (legacy fallback)."""
    cmd = [
        "claude",
        "--dangerously-skip-permissions",
        "--model", model,
        "--system-prompt", CLAUDE_SYSTEM_PROMPT,
        "-p", "-",
    ]

    env = _make_env(CLAUDECODE=None, CLAUDE_CODE_ENTRYPOINT=None)

    print(f"[run_agent] Starting Claude CLI ({model}) for {agent_name}")
    print(f"[run_agent] System prompt: {len(CLAUDE_SYSTEM_PROMPT)} chars (cacheable)")
    print(f"[run_agent] User prompt: {len(user_prompt)} chars")
    result = subprocess.run(
        cmd,
        input=user_prompt,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(csc_root),
        env=env,
        capture_output=False,
    )
    return result.returncode


# Keep old name as alias for backward compatibility
run_claude = run_claude_cli


def run_gemini(agent_name: str, model: str, workorder_content: str, csc_root: Path):
    """Invoke Gemini CLI (installed locally, not via npx).

    On Windows, Gemini CLI's node-pty requires a console (conpty).
    We write workorder to a temp file and use a wrapper batch script
    that runs in its own console window, redirecting output back to stdout.
    """
    gemini_cli = shutil.which("gemini") or shutil.which("gemini-cli")
    if not gemini_cli:
        print("[run_agent] ERROR: gemini not found in PATH (run: npm install -g @google/gemini-cli)")
        return 1

    import tempfile
    is_windows = os.name == "nt"

    # Write workorder to temp file
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".md", prefix="gemini_wo_")
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            f.write(workorder_content)

        env = _make_env()

        if is_windows:
            # On Windows, gemini-cli's node-pty needs a console.
            # CREATE_NEW_CONSOLE gives it one; we capture output via PIPE
            # and relay it to our stdout (which queue-worker logs to file).
            cmd = [gemini_cli, "-y", "--sandbox=none",
                   "-m", model, "-p", " "]
            print(f"[run_agent] Starting Gemini ({model}) for {agent_name}")
            sys.stdout.flush()
            proc = subprocess.Popen(
                cmd,
                stdin=open(tmp_path, "r", encoding="utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(csc_root),
                env=env,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
            # Relay output line by line to our stdout
            for line in proc.stdout:
                sys.stdout.write(line)
                sys.stdout.flush()
            proc.wait()
            result = type("R", (), {"returncode": proc.returncode})()
        else:
            cmd = [gemini_cli, "-y", "-m", model, "-p", " "]
            print(f"[run_agent] Starting Gemini ({model}) for {agent_name}")
            result = subprocess.run(
                cmd,
                input=workorder_content,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(csc_root),
                env=env,
                capture_output=False,
            )
        return result.returncode
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def run_local(agent_name: str, model: str, workorder_content: str, csc_root: Path):
    """Invoke local model via ollama CLI."""
    ollama = shutil.which("ollama")
    if not ollama:
        print("[run_agent] ERROR: ollama not found in PATH")
        return 1

    cmd = [ollama, "run", model]

    print(f"[run_agent] Starting local model ({model}) for {agent_name}")
    result = subprocess.run(
        cmd,
        input=workorder_content,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(csc_root),
        env=_make_env(),
        capture_output=False,
    )
    return result.returncode


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: run_agent.py <workorder-path>")
        sys.exit(1)

    workorder_path = Path(sys.argv[1])
    if not workorder_path.exists():
        print(f"ERROR: Workorder not found: {workorder_path}")
        sys.exit(1)

    agent_name = detect_agent_name(workorder_path)
    csc_root = find_csc_root(workorder_path)

    # Read workorder content (orders.md)
    try:
        workorder_content = workorder_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"ERROR: Cannot read workorder: {e}")
        sys.exit(1)

    # Extract WIP file path from orders.md
    wip_path = None
    try:
        match = re.search(r'ops/wo/wip/([^\s\n]+\.md)', workorder_content)
        if match:
            wip_filename = match.group(1)
            wip_path = csc_root / "workorders" / "wip" / wip_filename
    except Exception:
        pass

    wip_relative = f"ops/wo/wip/{wip_path.name}" if wip_path else "ops/wo/wip/task.md"

    print(f"[run_agent] Agent: {agent_name}, Root: {csc_root}, WIP: {wip_path.name if wip_path else 'unknown'}")

    # Git pull to get the orders.md and WIP files that queue-worker just pushed
    print(f"[run_agent] Git pull to get work files...")
    try:
        subprocess.run(["git", "pull"], cwd=str(csc_root), capture_output=True, text=True, timeout=60)
        print(f"[run_agent] Git pull complete")
    except Exception as e:
        print(f"[run_agent] WARNING: Git pull failed: {e}")

    # Build user prompt — minimal, just references the files to read
    # For Anthropic agents: static instructions are in the system prompt (cached)
    # For all agents: the user prompt just tells them WHAT to work on
    user_prompt = f"""Your task file is: {wip_relative}
Read it now and complete the work described in it.

Your orders file is: agents/{agent_name}/queue/work/orders.md
Read it for procedures and orientation.

Journal every step to {wip_relative} using: python bin/next_step {wip_relative} "description"
Start with: python bin/next_step {wip_relative} START
End with: python bin/next_step {wip_relative} COMPLETE
"""

    # For non-Anthropic agents, inline the full content since they may lack file tools
    if agent_name not in ANTHROPIC_AGENTS:
        wip_content = ""
        if wip_path and wip_path.exists():
            try:
                wip_content = wip_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                pass
        user_prompt = f"""# Task

Read and complete this workorder:

## WIP File: {wip_relative}
```
{wip_content}
```

## Orders: agents/{agent_name}/queue/work/orders.md
```
{workorder_content}
```

## Instructions
1. Complete the task described in the WIP file
2. Journal each step to {wip_relative} BEFORE doing it
3. When complete, append "COMPLETE" as the last line
4. Do NOT move files, run tests, or modify git
"""

    # Route to correct runner
    if agent_name in ANTHROPIC_AGENTS:
        model = ANTHROPIC_AGENTS[agent_name]
        # Use Anthropic API by default; set CSC_USE_CLAUDE_CLI=1 for old behavior
        if os.environ.get("CSC_USE_CLAUDE_CLI") == "1":
            print(f"[run_agent] CSC_USE_CLAUDE_CLI=1, using Claude Code CLI")
            rc = run_claude_cli(agent_name, model, user_prompt, csc_root)
        else:
            rc = run_anthropic_api(agent_name, model, user_prompt, csc_root)
    elif agent_name in GEMINI_AGENTS:
        model = GEMINI_AGENTS[agent_name]
        rc = run_gemini(agent_name, model, user_prompt, csc_root)
    elif agent_name in LOCAL_AGENTS:
        model = LOCAL_AGENTS[agent_name]
        rc = run_local(agent_name, model, user_prompt, csc_root)
    else:
        # Unknown agent — try Anthropic API with haiku as default
        print(f"[run_agent] WARNING: Unknown agent '{agent_name}', defaulting to haiku via API")
        rc = run_anthropic_api(agent_name, "claude-haiku-4-5-20251001", user_prompt, csc_root)

    # Trigger queue-worker to process completion and pull next workorder
    try:
        subprocess.run(["csc-ctl", "cycle", "queue-worker"], timeout=30, capture_output=True)
    except Exception as e:
        print(f"[run_agent] Note: queue-worker trigger failed: {e}")

    sys.exit(rc)


if __name__ == "__main__":
    main()
