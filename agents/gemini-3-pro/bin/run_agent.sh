#!/bin/bash
#
# run_agent.sh - Gemini agent startup script for Unix-like systems
# For: gemini, gemini-2.5-flash, gemini-3-flash, gemini-3-pro, etc.
# Uses: gemini -y -m <model> -p " " < stdin
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
  # Walk up from AGENT_ROOT looking for csc-service.json
  CSC_ROOT="$AGENT_ROOT"
  for i in 1 2 3 4 5 6 7 8; do
    CSC_ROOT="$(dirname "$CSC_ROOT")"
    if [ -f "$CSC_ROOT/csc-service.json" ]; then
      break
    fi
  done
fi

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
    echo "ERROR: Workorder not found: $WORKORDER_PATH (tried $CSC_ROOT/$WORKORDER_PATH)"
    exit 1
  fi
else
  echo "ERROR: No workorder specified"
  exit 1
fi

# Find template (agent-specific first, then ops/agents/templates)
TEMPLATE="$AGENT_ROOT/orders.md-template"
if [ ! -f "$TEMPLATE" ]; then
  TEMPLATE="$CSC_ROOT/ops/agents/templates/orders.md-template"
fi
if [ ! -f "$TEMPLATE" ]; then
  TEMPLATE="$CSC_ROOT/agents/templates/orders.md-template"
fi

if [ ! -f "$TEMPLATE" ]; then
  echo "ERROR: No template found (checked $AGENT_ROOT/orders.md-template, ops/agents/templates/)"
  exit 1
fi

# Create logs directory (in ops/logs/ if available, else CSC_ROOT/logs/)
if [ -d "$CSC_ROOT/ops/logs" ] || mkdir -p "$CSC_ROOT/ops/logs" 2>/dev/null; then
  LOGS_DIR="$CSC_ROOT/ops/logs"
else
  LOGS_DIR="$CSC_ROOT/logs"
  mkdir -p "$LOGS_DIR"
fi
LOG_FILE="$LOGS_DIR/${AGENT_NAME}_$(date +%s).log"

# Build prompt from template + orders.md content
TEMPLATE_CONTENT=$(cat "$TEMPLATE")
WORKORDER_CONTENT=$(cat "$WORKORDER_PATH")
FULL_PROMPT="$TEMPLATE_CONTENT

$WORKORDER_CONTENT"

# Agents run directly in CSC_ROOT (no temp clone) to access all submodule content
echo "Invoking: gemini -y -m $MODEL -p \" \""
cd "$CSC_ROOT"
echo "$FULL_PROMPT" | \
  gemini -y -m "$MODEL" -p " " \
  2>&1 | tee "$LOG_FILE"

echo ""
echo "[INFO] Agent execution completed"
echo "[INFO] Log: $LOG_FILE"
