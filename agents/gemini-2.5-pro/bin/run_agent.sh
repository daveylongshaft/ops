#!/bin/bash
#
# run_agent.sh - Gemini agent startup script for Unix-like systems
# For: gemini, gemini-2.5-flash, gemini-3-flash, gemini-3-pro, etc.
# Uses: gemini-cli -y -m <model> -p " " < stdin
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_ROOT="$(dirname "$SCRIPT_DIR")"
AGENT_NAME="$(basename "$AGENT_ROOT")"
CSC_ROOT="$(cd "$AGENT_ROOT/../.." && pwd)"

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
    gemini-3-pro) MODEL="gemini-2.5-pro" ;;
    gemini-3-flash) MODEL="gemini-2.5-flash" ;;
    gemini-2.5-flash*) MODEL="gemini-2.5-flash" ;;
    gemini) MODEL="gemini-2.5-pro" ;;
    *) MODEL="gemini-2.5-pro" ;;
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

# Check npx availability
if ! command -v npx &>/dev/null; then
  echo "ERROR: npx not found (required for Gemini CLI)"
  exit 1
fi

# Create agent working directory under temp (NOT in agents dir)
WORK_DIR="${TMPDIR:-/tmp}/csc-agent-$AGENT_NAME"
if [ ! -d "$WORK_DIR" ]; then
  echo "Creating agent work directory: $WORK_DIR"
  git clone "$CSC_ROOT" "$WORK_DIR" 2>/dev/null || {
    mkdir -p "$WORK_DIR"
    cp -r "$CSC_ROOT"/{packages,tools,workorders,agents,tests,bin,.env,README.md,CLAUDE.md,csc-service.json} "$WORK_DIR/" 2>/dev/null || true
  }
else
  # Pull latest changes
  cd "$WORK_DIR" && git pull --rebase 2>/dev/null || true
  cd "$CSC_ROOT"
fi

# Invoke Gemini CLI from work directory
echo "Invoking: gemini-cli -y -m $MODEL -p \" \""
cd "$WORK_DIR"
echo "$FULL_PROMPT" | \
  gemini-cli -y -m "$MODEL" -p " " \
  2>&1 | tee "$LOG_FILE"

echo ""
echo "[INFO] Agent execution completed"
echo "[INFO] Log: $LOG_FILE"
