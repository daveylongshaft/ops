# Prompt 3: Integrate Aider with dc-agent-wrapper

## Task

Verify and fix aider-agent integration with dc-agent-wrapper if needed.

**Depends on**: Prompt 2 must succeed first.

## Requirements

1. Verify dc-agent-wrapper properly routes to aider-agent:
   - Check build_agent_cmd() function recognizes 'aider-agent'
   - Check it passes model name correctly
   - Check stdin usage is enabled

2. Test the integration by running aider-agent via dc-agent-wrapper:
   - Create a simple test task in prompts/ready/
   - Move it to prompts/wip/ manually
   - Run: python3 bin/dc-agent-wrapper TASK.md aider-agent codellama:7b /tmp/log.txt prompts/wip/TASK.md
   - Verify it completes

3. Fix any issues found:
   - Model name formatting (should be ollama/MODEL)
   - Flag handling
   - Timeout settings
   - stdin/stdout piping

## Acceptance

- dc-agent-wrapper correctly recognizes aider-agent
- Successfully calls aider-agent with proper arguments
- Test task runs to completion
- Exit code 0 on success

## Work Log

Integrating aider-agent with wrapper...
