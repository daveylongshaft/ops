# Update Documentation and Verify System

## Objective

Update project documentation to reference `agent-wrapper` and verify the complete system works end-to-end.

## Context

Final step: Update all documentation references and perform comprehensive testing of the new agent-wrapper with template system.

## Tasks

### 1. Update CLAUDE.md

**File:** `CLAUDE.md`

**Find and replace:**
- [x] All instances of `dc-agent-wrapper` → `agent-wrapper`

**Key sections to check:**
- Git workflow section
- Background services section
- Command examples
- File locations table

### 2. Update Memory Files

**File:** `C:\Users\davey\.claude\projects\C--csc\memory\MEMORY.md`

**Add new section:**

```markdown
## Agent Wrapper System

The universal `agent-wrapper` (formerly `dc-agent-wrapper`, now removed) handles:
- Template-based queue integration
- Git operations (pull, commit, push, refresh-maps)
- COMPLETE marker detection
- Prompt lifecycle (ready → wip → done/ready)

Templates in `agents/templates/` are copied to `agents/<agent>/queue/in/` with variable substitution for standardized task files.
```

### 3. Comprehensive Testing

**A. Template Creation Test:**

```bash
# Verify template system exists
ls -la agents/templates/
cat agents/templates/default.md | grep '{prompt_name}'
```

**B. Queue Integration Test:**

```bash
# Create test prompt
echo "# Test agent wrapper" > prompts/ready/test-wrapper-system.md

# Assign to agent (triggers template copy)
agent select haiku
agent assign test-wrapper-system.md

# Verify template in queue
ls -la agents/haiku/queue/in/
cat agents/haiku/queue/in/test-wrapper-system.md

# Check for variable substitution (no {placeholders})
cat agents/haiku/queue/in/test-wrapper-system.md | grep -E '\{(prompt_name|agent_name|timestamp|model)\}' && echo "FAIL: Placeholders not substituted" || echo "PASS: Variables substituted"
```

**C. Full Integration Test:**

```bash
# Create benchmark prompt
benchmark add test-wrapper-integration "Write a test function"

# Run with agent
benchmark run test-wrapper-integration haiku

# Monitor logs
tail -f logs/agent_*.log

# Verify prompt moved to done
ls -la prompts/done/benchmark-test-wrapper-integration-*.md
```

**D. Cross-Platform Test (Windows):**

```bash
# Verify .bat wrapper exists
ls -la bin/agent-wrapper.bat

# Test wrapper invocation
python bin/agent-wrapper --help 2>&1 | grep "Usage: agent-wrapper"
```

**E. Backward Compatibility Test:**

```bash
# Verify old wrapper still exists


# Queue worker can find wrapper
queue-worker cycle 2>&1 | grep "Found wrapper.*agent-wrapper"
```

### 4. Verification Checklist

Run through complete checklist:

```bash
# 1. Template system
test -f agents/templates/default.md && echo "✓ Template exists" || echo "✗ Template missing"

# 2. Wrapper renamed
test -f bin/agent-wrapper && echo "✓ Wrapper exists" || echo "✗ Wrapper missing"

# 3. Template copy function
grep -q "copy_template_to_queue" bin/agent-wrapper && echo "✓ Function exists" || echo "✗ Function missing"

# 4. Queue mode support
grep -q "queue_mode.*=.*--queue-mode" bin/agent-wrapper && echo "✓ Queue mode exists" || echo "✗ Queue mode missing"

# 5. Agent service updated
grep -q "agent-wrapper" packages/csc-shared/services/agent_service.py && echo "✓ Service updated" || echo "✗ Service not updated"

# 6. Queue worker updated
grep -q "agent-wrapper" packages/csc-shared/services/queue_worker_service.py && echo "✓ Worker updated" || echo "✗ Worker not updated"

# 7. Documentation updated
grep -q "agent-wrapper" CLAUDE.md && echo "✓ Docs updated" || echo "✗ Docs not updated"
```

## Completion Criteria

- [x] CLAUDE.md updated (all dc-agent-wrapper → agent-wrapper)
- [ ] Memory files updated with agent wrapper section
- [ ] Template creation test passes
- [ ] Queue integration test passes (template appears in queue/in/)
- [ ] Variable substitution test passes (no placeholders remain)
- [ ] Full integration test passes (benchmark completes)
- [ ] Cross-platform test passes (Windows .bat works)
- [ ] Backward compatibility test passes (old wrapper still exists)
- [ ] All 7 verification checklist items pass
- [ ] No regressions in existing agent workflows

## Final Verification

```bash
# Run complete system test
echo "# Final integration test" > prompts/ready/final-test.md
agent select haiku
agent assign final-test.md
sleep 5
ls -la agents/haiku/queue/in/final-test.md
cat agents/haiku/queue/in/final-test.md | head -20
```

**Expected output:**
- Template file exists in queue/in/
- Contains "Agent Task: Final Integration Test" (title case, no underscores)
- References `prompts/wip/final-test.md`
- References `README.1shot`
- All variables substituted (no {placeholders})
- Timestamp in ISO format
- PID shows "pending"

1. Check CLAUDE.md updated
2. Verify templates directory
3. Verify wrapper executable
4. Test template substitution
