#!/bin/bash
# generate_orders_md.sh
# Generates the orders.md file for an agent's queue/in directory.
# Takes AGENT_DIR and WO_FILENAME (must be in workorders/wip/) as arguments.

AGENT_DIR="$1"
# Optional 3rd arg: WIP dir prefix (default: workorders/wip)
# Pass ops/wo/wip for the submodule layout
WIP_DIR_PREFIX="${3:-workorders/wip}"
WIP_RELATIVE_PATH="$WIP_DIR_PREFIX/$2"
TEMPLATE_PATH="$AGENT_DIR/orders.md-template"

echo "usage: generate_orders_md.sh <agent_dir> <wo_filename> (must be in workorders/wip/)"
echo "generating \"$AGENT_DIR/queue/in/orders.md\" for $WIP_RELATIVE_PATH"

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

# Generate content by replacing the tag using sed
OUTPUT_FILE="$AGENT_DIR/queue/in/orders.md"
sed "s|<wip_file_relative_pathspec>|$WIP_RELATIVE_PATH|g" "$FINAL_TEMPLATE" > "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo "Successfully generated $OUTPUT_FILE"
else
    echo "ERROR: Failed to generate $OUTPUT_FILE" >&2
    exit 1
fi
