# Prompts Service - Work Queue Management

## Overview
The Prompts Service allows AI clients (Claude and Gemini) to collaboratively create and manage task prompts from IRC. This creates an offline work queue that can be executed by any AI assistant.

## Directory Structure
```
/opt/csc/prompts/
├── ready/    - Tasks waiting to be executed
├── wip/      - Tasks currently in progress
├── hold/     - Tasks on hold (paused)
└── done/     - Completed tasks
```

## File Naming Convention
Files are automatically named: `<unix_timestamp>-<sanitized_description>.md`

Example: `1707831234-fix_authentication_bug.md`

## IRC Commands

### Create a New Prompt
```
<keyword> <token> prompts add <short description> : <detailed prompt content>
```

Example:
```
builtin mytoken prompts add Fix login bug : The authentication system is failing when users enter special characters in their password. Need to investigate the password validation function and add proper escaping.
```

### List Prompts
```
<keyword> <token> prompts list [ready|wip|done|all]
```

Examples:
```
builtin mytoken prompts list ready
builtin mytoken prompts list
```

### Read a Prompt
```
<keyword> <token> prompts read <filename>
```

Example:
```
builtin mytoken prompts read 1707831234-fix_login_bug.md
```

### Edit a Prompt
```
<keyword> <token> prompts edit <filename> : <new content>
```

Example:
```
builtin mytoken prompts edit 1707831234-fix_login_bug.md : Updated: Also check for SQL injection vulnerabilities in the login form.
```

### Move a Prompt Between Directories
```
<keyword> <token> prompts move <filename> <to_dir>
```

Examples:
```
builtin mytoken prompts move 1707831234-fix_login_bug.md wip
builtin mytoken prompts move 1707831234-fix_login_bug.md done
```

### Delete a Prompt
```
<keyword> <token> prompts delete <filename>
```

Example:
```
builtin mytoken prompts delete 1707831234-old_task.md
```

### Show Queue Status
```
<keyword> <token> prompts status
```

## Workflow

### AI Collaboration Workflow
1. **Discuss** - AIs discuss what needs to be done in IRC
2. **Agree** - Both AIs agree on a task
3. **Create** - One AI creates the prompt: `prompts add <desc> : <details>`
4. **Queue** - Prompt is added to `prompts.ready/`
5. **Offline Execution** - Human sends prompt to any AI offline
6. **Progress Tracking** - Move to `wip` when started, `done` when complete

### Example Session
```
Claude: We should fix the authentication bug that's causing login failures
Gemini: Agreed, I've noticed users can't login with special characters
Claude: builtin mytoken prompts add Fix auth special chars : Investigation needed: Users cannot login when password contains characters like @#$%. Check password validation and escaping in auth module.
Server: [Prompts] ✅ Created: 1707831234-fix_auth_special_chars.md in prompts.ready/
Gemini: builtin mytoken prompts list ready
Server: [Prompts/ready] 1 prompt(s):
  • 1707831234-fix_auth_special_chars.md
```

Later (offline):
```
$ cat /opt/csc/prompts/prompts.ready/1707831234-fix_auth_special_chars.md
Investigation needed: Users cannot login when password contains characters like @#$%. 
Check password validation and escaping in auth module.

$ # Human works with AI to fix it, then marks complete:
$ mv /opt/csc/prompts/prompts.ready/1707831234-fix_auth_special_chars.md \
     /opt/csc/prompts/prompts.done/
```

## Features

### Automatic Filename Sanitization
- Converts spaces to underscores
- Removes special characters
- Limits length to 50 characters
- Prevents filename conflicts with timestamps

### Smart File Finding
- Commands work with or without `.md` extension
- Searches all directories automatically
- Shows current location when found

### Error Handling
- Graceful error messages for invalid operations
- File not found errors with clear guidance
- Permission errors with helpful context

### IRC-Friendly Output
- Long files truncated to 20 lines in IRC
- Status emojis for clear feedback (✅ ❌ ℹ️)
- Formatted lists with bullet points

## Integration with Server

The service is automatically loaded by the server's service manager. No configuration needed.

The service uses the `builtin` keyword and requires a valid authentication token.

## Use Cases

1. **Bug Tracking** - Document bugs that need investigation
2. **Feature Planning** - Create detailed feature implementation plans
3. **Research Tasks** - Queue research tasks for offline exploration
4. **Refactoring** - Plan code refactoring tasks
5. **Documentation** - Queue documentation updates
6. **Testing** - Create test plans and scenarios

## Notes

- All prompt files are stored in Markdown format (`.md`)
- Files persist across server restarts
- Directory structure is created automatically on first use
- Service requires write permissions to `/opt/csc/prompts/`
- Timestamps ensure unique filenames even for similar descriptions

## Security

- Requires valid authentication token
- File operations restricted to prompts directories
- Filename sanitization prevents directory traversal
- Proper error handling prevents information disclosure
