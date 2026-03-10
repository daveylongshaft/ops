#!/bin/bash
#
# run_agent.sh - Local agent runner for deepseek (uses cagent exec)
#
# Usage: run_agent.sh <path-to-orders.md>
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_ROOT="$(dirname "$SCRIPT_DIR")"
AGENT_NAME="$(basename "$AGENT_ROOT")"
CSC_ROOT="$(cd "$AGENT_ROOT/../.." && pwd)"

# Load .env
if [ -f "$CSC_ROOT/.env" ]; then
  set -a
  source "$CSC_ROOT/.env"
  set +a
fi

WORKORDER_PATH="${1:-}"

if [ -z "$WORKORDER_PATH" ]; then
  echo "ERROR: workorder path required"
  exit 1
fi

# If relative path, resolve from CSC_ROOT
if [ ! -f "$WORKORDER_PATH" ] && [ -f "$CSC_ROOT/$WORKORDER_PATH" ]; then
  WORKORDER_PATH="$CSC_ROOT/$WORKORDER_PATH"
fi

if [ ! -f "$WORKORDER_PATH" ]; then
  echo "ERROR: Workorder not found: $WORKORDER_PATH"
  exit 1
fi

YAML_PATH="$AGENT_ROOT/cagent.yaml"
if [ ! -f "$YAML_PATH" ]; then
  echo "ERROR: cagent.yaml not found at $YAML_PATH"
  exit 1
fi

CAGENT_BIN=$(command -v cagent 2>/dev/null || echo "")
if [ -z "$CAGENT_BIN" ]; then
  echo "ERROR: cagent not found in PATH"
  exit 1
fi

# Read workorder content
WORKORDER_CONTENT=$(cat "$WORKORDER_PATH")

echo "[run_agent] Starting cagent exec for $AGENT_NAME"
echo "[run_agent] YAML: $YAML_PATH"
echo "[run_agent] Workorder: $WORKORDER_PATH"

# Invoke cagent with the YAML config
echo "$WORKORDER_CONTENT" | "$CAGENT_BIN" exec "$YAML_PATH" --working-dir "$CSC_ROOT" 2>&1

echo ""
echo "[INFO] Agent execution completed"
