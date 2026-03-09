# Prompt 4: End-to-End dc-run Test

## Task

Test the complete workflow from dc-run command to task completion.

**Depends on**: Prompts 1-3 must be complete.

## Workflow Test

1. List available prompts:
   ```bash
   dc-run list
   ```

2. Create a simple test prompt in prompts/ready/ if not already there
   - Task: "Create a file named _agent_test_marker.txt in /app with content 'test successful'"
   - Name: test-aider-simple.md

3. Run via dc-run:
   ```bash
   dc-run test-aider-simple.md --agent aider-agent --model codellama:7b
   ```

4. Verify workflow:
   - Prompt moves from ready/ → wip/
   - aider-agent runs
   - Changes are made (file created)
   - Prompt moves from wip/ → done/ (if exit code 0)
   - OR stays in wip/ if exit code non-zero

5. Check results:
   - File _agent_test_marker.txt exists in project root
   - Content is "test successful"
   - Prompt is in done/ directory
   - Git has uncommitted changes (or already committed)

## Acceptance

- Full workflow completes without errors
- Prompt moves to done/
- Changes are visible in the codebase
- Ready for production use

## Issues to Document

- If any step fails, note where and why
- Any timeout issues?
- Any model/ollama issues?
- Any git workflow issues?

## Work Log

Running end-to-end dc-run test...
