# Debugging Process: Qwen Integration

## Step 1: Check Logs
Look at recent agent logs to see error messages:
```bash
tail -20 /c/csc/logs/agent_1771658633_benchmark-hello-world-1771651430.log
```
Look for: exit code, error messages, ollama connection issues

## Step 2: Test Ollama Directly
Verify ollama service is running and responding:
```bash
curl http://localhost:11434/api/tags
```
Should return list of models including qwen2.5-coder:7b

## Step 3: Test Agent Binary
Try calling ollama-agent directly with a simple input:
```bash
echo "Hello test" | /c/csc/bin/ollama-agent.BAT -y -m qwen2.5-coder:7b -p -
```
Should run without error and return output

## Step 4: Check Agent Wrapper
Trace the exact command being built:
- Look at build_agent_cmd() function in `/c/csc/bin/agent-wrapper`
- Verify the -p - flag is present for ollama agents

## Step 5: Manual Assignment Test
Create a simple test prompt and try agent assign:
```bash
echo "# Test prompt
Just echo hello" > /c/csc/workorders/ready/test-qwen.md
agent assign test-qwen.md ollama-qwen
sleep 5
agent tail 10
```
Check if prompt ends up in done/ (success) or ready/ (failure)

## Common Issues and Fixes

### Ollama Service Not Running
- Start ollama: `ollama serve` (on another terminal)
- Or check if it's already running

### Model Not Loaded
- Check available models: `ollama list`
- If qwen2.5-coder:7b not listed, pull it: `ollama pull qwen2.5-coder:7b`

### Input Format Issue
- Verify -p - is being passed correctly
- Check if ollama-agent script properly reads from stdin

### Wrapper Command Issue
- Trace what command agent-wrapper actually builds
- Check agent_service.py to verify wrapper path is correct

## What NOT to Do
- Don't modify the wrapper code yourself - only diagnose
- Don't run tests
- Don't touch git
- Just focus on finding and fixing the root cause
