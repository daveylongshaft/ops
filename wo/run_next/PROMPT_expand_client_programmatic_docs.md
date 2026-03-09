# Expand Client Programmatic Mode Documentation

## Task
Expand and enhance the programmatic mode documentation in `/opt/csc/docs/client.md` to provide comprehensive guidance on using the client for automated, headless operations. This is critical for the AI task execution system which relies on scripting the client.

## Context
The client currently has basic programmatic docs (lines 22-34 in client.md), but these need significant expansion because:
- README.1st mandates that "All AI-related tasks must be performed using the CSC Client in programmatic mode"
- Developers need clear examples for common patterns (task assignment, command sequencing, output capture)
- Error handling and verification procedures are not documented
- Integration with the prompt/agent dispatch system is missing

## Requirements

### 1. Expand the "Programmatic Usage" Section
Add comprehensive coverage with:

**a) Detailed flag documentation:**
- Explain `--infile` with examples (sequential commands, file format)
- Explain `--outfile` and output capture
- Explain `--detach` and implications for exit codes, logging
- Show how to combine flags for different use cases

**b) Common patterns with examples:**
```
Pattern 1: Simple sequential commands
Pattern 2: Capturing output for verification
Pattern 3: Error detection and response
Pattern 4: Task assignment workflow
Pattern 5: Long-running operations with detach
```

**c) Best practices:**
- How to structure infiles for reliability
- Timeout considerations
- Exit code handling
- Logging and debugging

### 2. Add a New Section: "Task Assignment via Programmatic Mode"
This section should show:
- The standard workflow for assigning AI agents to tasks using the client
- Example of a complete task assignment sequence
- Integration with `/join`, `AI agent assign` command pattern
- How to verify success by parsing output

**Example structure:**
```bash
# Create infile
cat > task_cmds.txt <<'EOF'
/join #general
AI agent assign PROMPT_task_name.md
/quit
EOF

# Run client
python packages/csc_client/client.py --infile task_cmds.txt --outfile task_out.txt --detach

# Verify
grep -q "Agent assigned" task_out.txt && echo "Success" || echo "Failed"
```

### 3. Add Examples for Common Scenarios
- Joining multiple channels and sending messages
- File uploads in programmatic mode
- Service command execution
- Batch operations with multiple sequences

### 4. Error Handling & Debugging
- How to detect connection errors from output
- How to interpret client exit codes
- Logging troubleshooting tips
- Recovery strategies

## Acceptance Criteria
✅ Programmatic section expanded from ~12 lines to ~80-100 lines with clear subsections
✅ At least 5 working code examples with explanation
✅ New "Task Assignment" section with end-to-end example
✅ Best practices documented
✅ Error handling section added
✅ All examples reference actual CSC commands (not hypothetical)
✅ Documentation links back to related sections (file upload, services)

## Files to Modify
- `/opt/csc/docs/client.md` - Expand programmatic section starting at line 22

## Testing
After editing, verify:
1. Markdown syntax is valid
2. Examples are copy-pasteable
3. Links between sections work
4. No breaking changes to existing sections

## Resources
- README.1st (programmatic mode requirement)
- CLAUDE.md project instructions (AI task execution)
- Current client.py implementation (line 37-50: main entry with config handling)
read current client.md (lines 1-114)
read client.py (first 80 lines)
search for AI agent assign pattern
read README.1st (lines 90-106 show AI task execution pattern)
expand programmatic section: replaced lines 22-34 with comprehensive 360-line expanded section
verify markdown syntax and count lines
verify markdown: 48 code blocks, 45 H2 sections, 36 H3 subsections, all balanced
commit changes to git
commit completed: b407606
move to done/
