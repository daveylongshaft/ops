# Validation Checklist: Qwen Integration

## After Each Fix, Verify These Steps

### 1. Agent Binary Works
```bash
echo "Hello test" | /c/csc/bin/ollama-agent.BAT -y -m qwen2.5-coder:7b -p -
```
✓ Should complete without error
✓ Should produce some output (response from model)

### 2. Simple Assignment Works
```bash
echo "# Quick test
Please respond with just the word: hello" > /c/csc/workorders/ready/test-qwen.md
agent assign test-qwen.md ollama-qwen
sleep 10
agent tail 5
```
✓ Prompt should move to done/ (not back to ready/)
✓ Work log should show completion

### 3. Benchmark Runs
```bash
agent assign benchmark-hello-world-1771651645.md ollama-qwen
sleep 20
agent tail 10
```
✓ Prompt should move to done/
✓ No error messages in tail

### 4. Full Benchmark Validation
Run 3 times to verify consistency:
```bash
for i in 1 2 3; do
  agent assign benchmark-hello-world-1771651645.md ollama-qwen
  sleep 20
  result=$(agent tail 1 | grep -c "done")
  if [ "$result" -eq 1 ]; then
    echo "Run $i: PASS"
  else
    echo "Run $i: FAIL"
  fi
done
```
✓ All 3 runs should show PASS

## Final Verification
- [ ] ollama service is running
- [ ] Model qwen2.5-coder:7b is loaded
- [ ] ollama-agent responds to stdin input
- [ ] agent assign moves prompts to done/ correctly
- [ ] Benchmark runs 3 times successfully
- [ ] No errors in logs

## If Validation Fails
- Check agent_tail output for error details
- Look at /c/csc/logs/agent_*.log for root cause
- Verify fix addresses the specific error
- Re-test after fix
