#!/usr/bin/env python3
"""
Universal agent runner — detects agent type from directory name and
invokes the correct AI CLI (Claude Code, Gemini CLI, etc.).

Usage: run_agent.py <path-to-orders.md>

The agent name is derived from the grandparent directory:
    agents/<agent-name>/bin/run_agent.py
              ↑ this becomes the agent name

Cross-platform: works on Windows, Linux, macOS, Android/Termux.
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path


# ---------------------------------------------------------------------------
# Agent → CLI mapping
# ---------------------------------------------------------------------------

# Claude models: use Claude Code CLI
CLAUDE_AGENTS = {
    "haiku":   "claude-haiku-4-5-20251001",
    "sonnet":  "claude-sonnet-4-5-20250929",
    "opus":    "claude-opus-4-6",
    "claude":  "claude-sonnet-4-5-20250929",
}

# Gemini models: use Gemini CLI via npx
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


def run_claude(agent_name: str, model: str, workorder_content: str, csc_root: Path):
    """Invoke Claude Code CLI."""
    cmd = [
        "claude",
        "--dangerously-skip-permissions",
        "--model", model,
        "-p", "-",
    ]

    env = _make_env(CLAUDECODE=None, CLAUDE_CODE_ENTRYPOINT=None)

    print(f"[run_agent] Starting Claude ({model}) for {agent_name}")
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


def run_gemini(agent_name: str, model: str, workorder_content: str, csc_root: Path):
    """Invoke Gemini CLI (installed locally, not via npx).

    On Windows, Gemini CLI's node-pty requires a console (conpty).
    We write workorder to a temp file and use a wrapper batch script
    that runs in its own console window, redirecting output back to stdout.
    """
    gemini_cli = shutil.which("gemini-cli")
    if not gemini_cli:
        print("[run_agent] ERROR: gemini-cli not found in PATH (run: npm install -g @google/gemini-cli)")
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

    # Read workorder content
    try:
        workorder_content = workorder_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"ERROR: Cannot read workorder: {e}")
        sys.exit(1)

    print(f"[run_agent] Agent: {agent_name}, Root: {csc_root}")

    # Route to correct CLI
    if agent_name in CLAUDE_AGENTS:
        model = CLAUDE_AGENTS[agent_name]
        rc = run_claude(agent_name, model, workorder_content, csc_root)
    elif agent_name in GEMINI_AGENTS:
        model = GEMINI_AGENTS[agent_name]
        rc = run_gemini(agent_name, model, workorder_content, csc_root)
    elif agent_name in LOCAL_AGENTS:
        model = LOCAL_AGENTS[agent_name]
        rc = run_local(agent_name, model, workorder_content, csc_root)
    else:
        # Unknown agent — try claude as default
        print(f"[run_agent] WARNING: Unknown agent '{agent_name}', defaulting to Claude haiku")
        rc = run_claude(agent_name, "claude-haiku-4-5-20251001", workorder_content, csc_root)

    sys.exit(rc)


if __name__ == "__main__":
    main()
