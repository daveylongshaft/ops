# Prompts CLI - Quick Reference

## Installation
✅ Installed at: `/usr/local/bin/prompts`
✅ Service module: `/opt/csc/services/prompts_service.py`
✅ Data directories: `/opt/csc/prompts/{ready,wip,hold,done}/`

## Basic Commands

### Create a New Task
```bash
prompts add <description> : <content>
```
Example:
```bash
prompts add "Fix auth bug" : "The login system fails when users enter special characters"
```

### List Tasks
```bash
prompts list              # List all
prompts list ready        # List ready tasks only
prompts list wip          # List in-progress tasks
prompts list hold         # List tasks on hold
prompts list done         # List completed tasks
```

### Read a Task
```bash
prompts read <filename>
```
Example:
```bash
prompts read 1770986998-fix_auth_bug.md
```

### Move Task Between States
```bash
prompts move <filename> <to_dir>
```
Examples:
```bash
prompts move 1770986998-fix_auth_bug.md wip    # Start working
prompts move 1770986998-fix_auth_bug.md done   # Mark complete
prompts move 1770986998-fix_auth_bug.md ready  # Move back to queue
prompts move 1770986998-fix_auth_bug.md hold   # Put on hold
```

### Hold Shortcut
```bash
prompts hold <filename>
```
Example:
```bash
prompts hold 1770986998-fix_auth_bug.md
```

### Edit a Task
```bash
prompts edit <filename> : <new_content>
```
Example:
```bash
prompts edit 1770986998-fix_auth_bug.md : "Updated: Also check for SQL injection"
```

### Delete a Task
```bash
prompts delete <filename>
```
Example:
```bash
prompts delete 1770986998-old_task.md
```

### Show Queue Status
```bash
prompts status
```
Output:
```
[Prompts] Status:
  📋 Ready: 1 task(s)
  🔄 In Progress: 0 task(s)
  ✅ Done: 0 task(s)
  📊 Total: 1 task(s)
```

### Get Help
```bash
prompts help
```

## Typical Workflow

### 1. Add a Task
```bash
prompts add "Implement user authentication" : "Create JWT-based authentication system with login/logout endpoints"
```

### 2. List Tasks
```bash
prompts list ready
```

### 3. Start Working on a Task
```bash
prompts move 1234567890-implement_user_authentication.md wip
```

### 4. Put Task on Hold (if needed)
```bash
prompts hold 1234567890-implement_user_authentication.md
```

### 5. Read Task Details While Working
```bash
prompts read 1234567890-implement_user_authentication.md
```

### 5. Complete the Task
```bash
prompts move 1234567890-implement_user_authentication.md done
```

### 6. Check Status
```bash
prompts status
```

## Tips

### Filename Shortcuts
- You can use filenames with or without `.md` extension
- The tool searches all directories automatically

### Multi-line Content
For long content, use command substitution:
```bash
prompts add "My task" : "$(cat my-task-details.txt)"
```

Or heredoc:
```bash
prompts add "My task" : "$(cat << 'ENDCONTENT'
Line 1
Line 2
Line 3
ENDCONTENT
)"
```

### Importing Existing Prompts
```bash
for file in /home/davey/.claude/prompts/ready/*.md; do
  name=$(basename "$file" .md)
  prompts add "$name" : "$(cat "$file")"
done
```

### Quick Status Check
Add to your shell alias:
```bash
alias pq='prompts status'
alias pl='prompts list ready'
```

## Integration with IRC Service

The CLI tool and IRC service use the same backend (`prompts_service.py`), so you can:
- Create prompts from CLI
- Manage them from IRC (via Claude/Gemini)
- Complete them offline
- All changes sync immediately

IRC commands:
```
builtin <token> prompts add <desc> : <content>
builtin <token> prompts list ready
builtin <token> prompts move <file> wip
builtin <token> prompts hold <file>
```

## File Locations

### Prompt Files
```
/opt/csc/prompts/
├── ready/  ← New tasks
├── wip/    ← In progress
├── hold/   ← Paused
└── done/   ← Completed
```

### File Naming
Format: `<unix_timestamp>-<sanitized_description>.md`

Example: `1770986998-realtime_session_persistence.md`

## Common Operations

### View All Ready Tasks
```bash
prompts list ready
```

### Start Working on First Task
```bash
file=$(prompts list ready | grep '•' | head -1 | awk '{print $2}')
prompts move $file wip
prompts read $file
```

### Complete Current Task
```bash
file=$(prompts list wip | grep '•' | head -1 | awk '{print $2}')
prompts move $file done
```

### Archive All Done Tasks
```bash
mkdir -p ~/prompts-archive/$(date +%Y-%m)
mv /opt/csc/prompts/prompts.done/*.md ~/prompts-archive/$(date +%Y-%m)/
```

## Error Handling

### Permission Denied
If you get permission errors:
```bash
sudo chmod -R 775 /opt/csc/prompts
sudo chown -R csc_user:csc_group /opt/csc/prompts
```

### Service Not Found
If import fails:
```bash
ls -la /opt/csc/services/prompts_service.py
```

### File Not Found
- Check filename spelling
- Try without `.md` extension
- Use `prompts list` to see available files
