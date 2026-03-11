#!/bin/bash
#
# run_agent.sh - Claude agent startup script for Unix-like systems
# For: haiku, sonnet, opus
# Uses: claude --dangerously-skip-permissions --model <model> -p -
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_ROOT="$(dirname "$SCRIPT_DIR")"
AGENT_NAME="$(basename "$AGENT_ROOT")"

# Resolve CSC_ROOT: prefer env var (set by queue_worker), else walk up to find csc-service.json
if [ -n "$CSC_ROOT" ] && [ -f "$CSC_ROOT/csc-service.json" ]; then
  : # Use env var
else
  CSC_ROOT="$AGENT_ROOT"
  for i in 1 2 3 4 5 6 7 8; do
    CSC_ROOT="$(dirname "$CSC_ROOT")"
    if [ -f "$CSC_ROOT/csc-service.json" ]; then
      break
    fi
  done
fi

# Clear Claude Code nesting detection so agents can spawn
unset CLAUDECODE
unset CLAUDE_CODE_ENTRYPOINT

# Load API keys from .env
if [ -f "$CSC_ROOT/.env" ]; then
  set -a
  source "$CSC_ROOT/.env"
  set +a
fi

# Parameters
WORKORDER_PATH="${1:-}"
MODEL="${2:-}"

# Set default models
if [ -z "$MODEL" ]; then
  case "$AGENT_NAME" in
    haiku) MODEL="haiku" ;;
    sonnet) MODEL="sonnet" ;;
    opus) MODEL="opus" ;;
    *) MODEL="unknown" ;;
  esac
fi

# Find workorder if not provided
if [ -z "$WORKORDER_PATH" ]; then
  QUEUE_IN="$AGENT_ROOT/queue/in"
  if [ -d "$QUEUE_IN" ]; then
    WORKORDER_PATH=$(ls "$QUEUE_IN"/*.md 2>/dev/null | head -1)
  fi
fi

# Validate workorder
if [ -n "$WORKORDER_PATH" ] && [ -f "$WORKORDER_PATH" ]; then
  :
elif [ -n "$WORKORDER_PATH" ]; then
  if [ -f "$CSC_ROOT/$WORKORDER_PATH" ]; then
    WORKORDER_PATH="$CSC_ROOT/$WORKORDER_PATH"
  else
    echo "ERROR: Workorder not found: $WORKORDER_PATH"
    exit 1
  fi
else
  echo "ERROR: No workorder specified"
  exit 1
fi

# Find template (agent-specific first, then ops/agents/templates/)
TEMPLATE="$AGENT_ROOT/orders.md-template"
if [ ! -f "$TEMPLATE" ]; then
  TEMPLATE="$CSC_ROOT/ops/agents/templates/orders.md-template"
fi
if [ ! -f "$TEMPLATE" ]; then
  echo "ERROR: No template found"
  exit 1
fi

# Create logs directory (in ops/logs/ if available)
if [ -d "$CSC_ROOT/ops/logs" ] || mkdir -p "$CSC_ROOT/ops/logs" 2>/dev/null; then
  LOGS_DIR="$CSC_ROOT/ops/logs"
else
  LOGS_DIR="$CSC_ROOT/logs"
  mkdir -p "$LOGS_DIR"
fi
LOG_FILE="$LOGS_DIR/${AGENT_NAME}_$(date +%s).log"

# Temp repo path (absolute) — agent runs from /opt, both /opt/clones and /opt/csc are in scope
WORK_DIR="${CSC_AGENT_REPO:-}"
AGENT_REPO_ABS="${WORK_DIR:-(no temp repo)}"

# Build prompt with placeholder substitution
TEMPLATE_CONTENT=$(cat "$TEMPLATE")
WORKORDER_CONTENT=$(cat "$WORKORDER_PATH")
FULL_PROMPT=$(printf '%s\n\n%s' "$TEMPLATE_CONTENT" "$WORKORDER_CONTENT" \
  | sed "s|<agent_repo_rel_path>|$AGENT_REPO_ABS|g")

# Find Claude binary
AGENT_BIN=$(command -v claude 2>/dev/null || echo "")
if [ -z "$AGENT_BIN" ]; then
  AGENT_BIN=$(find ~/.local/bin /usr/local/bin /usr/bin /opt/bin -name claude 2>/dev/null | head -1)
fi
if [ -z "$AGENT_BIN" ]; then
  echo "ERROR: claude binary not found"
  exit 1
fi

# Run from /opt so both /opt/clones (code repo) and /opt/csc (WO) are accessible
echo "Invoking: $AGENT_BIN --dangerously-skip-permissions --model $MODEL -p - (cwd: /opt, repo: $AGENT_REPO_ABS)"
cd /opt
echo "$FULL_PROMPT" | \
  "$AGENT_BIN" --dangerously-skip-permissions --model "$MODEL" -p - \
  2>&1 | tee "$LOG_FILE"

echo ""
echo "[INFO] Agent execution completed"
echo "[INFO] Log: $LOG_FILE"
