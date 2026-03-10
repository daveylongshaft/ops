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
CSC_ROOT="$(cd "$AGENT_ROOT/../.." && pwd)"

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

# Find template
TEMPLATE="$AGENT_ROOT/orders.md-template"
if [ ! -f "$TEMPLATE" ]; then
  TEMPLATE="$CSC_ROOT/agents/templates/default.md"
fi

if [ ! -f "$TEMPLATE" ]; then
  echo "ERROR: No template found"
  exit 1
fi

# Create logs directory
LOGS_DIR="$CSC_ROOT/logs"
mkdir -p "$LOGS_DIR"
LOG_FILE="$LOGS_DIR/${AGENT_NAME}_$(date +%s).log"

# Build prompt
TEMPLATE_CONTENT=$(cat "$TEMPLATE")
WORKORDER_CONTENT=$(cat "$WORKORDER_PATH")
FULL_PROMPT="$TEMPLATE_CONTENT

$WORKORDER_CONTENT"

# Find Claude binary
AGENT_BIN=$(command -v claude 2>/dev/null || echo "")
if [ -z "$AGENT_BIN" ]; then
  AGENT_BIN=$(find /usr/local/bin /usr/bin /opt/bin ~/.local/bin -name claude 2>/dev/null | head -1)
fi

if [ -z "$AGENT_BIN" ]; then
  echo "ERROR: claude binary not found"
  exit 1
fi

# Invoke Claude
echo "Invoking: $AGENT_BIN --dangerously-skip-permissions --model $MODEL -p -"
echo "$FULL_PROMPT" | \
  "$AGENT_BIN" --dangerously-skip-permissions --model "$MODEL" -p - \
  2>&1 | tee "$LOG_FILE"

echo ""
echo "[INFO] Agent execution completed"
echo "[INFO] Log: $LOG_FILE"
