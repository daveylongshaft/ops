#!/bin/bash
# generate_orders_md.sh
# Generates the orders.md file for an agent's queue/in directory.
# Takes AGENT_DIR and WO_FILENAME (must be in workorders/wip/) as arguments.

AGENT_DIR="$1"
# 3rd arg: absolute WIP file path (e.g. /opt/csc/ops/wo/wip/PROMPT_foo.md)
ABS_WIP_PATH="$3"
# 4th arg: agent repo relative path (relative to CSC_ROOT, e.g. tmp/gemini-2.5-pro/STEM-TS/repo)
AGENT_REPO_REL="${4:-}"
TEMPLATE_PATH="$AGENT_DIR/orders.md-template"

echo "usage: generate_orders_md.sh <agent_dir> <wo_filename> <abs_wip_path> [agent_repo_rel]"
echo "generating \"$AGENT_DIR/queue/in/orders.md\" for $ABS_WIP_PATH"

# Ensure output directory exists
mkdir -p "$AGENT_DIR/queue/in"

# Determine the actual template file to use
FINAL_TEMPLATE=""
if [ -f "$TEMPLATE_PATH" ]; then
    FINAL_TEMPLATE="$TEMPLATE_PATH"
else
    # Fallback to default template if agent-specific or provided template not found
    DEFAULT_TEMPLATE="agents/templates/orders.md-template"
    if [ -f "$DEFAULT_TEMPLATE" ]; then
        FINAL_TEMPLATE="$DEFAULT_TEMPLATE"
    else
        echo "ERROR: No template found at '$TEMPLATE_PATH' or default '$DEFAULT_TEMPLATE'." >&2
        exit 1
    fi
fi

# Generate content by replacing tags using sed
OUTPUT_FILE="$AGENT_DIR/queue/in/orders.md"
sed \
  -e "s|<wip_file_abs_path>|$ABS_WIP_PATH|g" \
  -e "s|<agent_repo_rel_path>|$AGENT_REPO_REL|g" \
  "$FINAL_TEMPLATE" > "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo "Successfully generated $OUTPUT_FILE"
else
    echo "ERROR: Failed to generate $OUTPUT_FILE" >&2
    exit 1
fi
