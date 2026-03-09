# CSC Project Map - Quick Reference

## Project Structure

```
csc/
├── bin/                    # CLI scripts & tools
│   ├── agent              # Agent management CLI
│   ├── prompts            # Workorder management CLI
│   └── queue-worker       # Queue processor (Python)
├── packages/
│   ├── csc-shared/        # Core library (IRC protocol, services)
│   ├── csc-server/        # IRC server
│   ├── csc-client/        # Human CLI client
│   ├── csc-claude/        # Claude AI client
│   ├── csc-gemini/        # Gemini AI client
│   └── csc-chatgpt/       # ChatGPT AI client
├── agents/                # Agent configs & queues
│   └── <name>/
│       ├── cagent.yaml    # Agent model config
│       ├── context/       # Agent-specific context files
│       └── queue/         # Work queue (in/work/out)
├── workorders/            # Workorder lifecycle
│   ├── ready/             # Waiting to be picked up
│   ├── wip/               # Currently being worked
│   └── done/              # Completed
├── tools/                 # Generated code maps
│   └── INDEX.txt          # Package overview
└── tests/                 # Test suite

```

## Key Files & What They Do

### Documentation
- **CLAUDE.md** - Main instructions for Claude Code agents
- **README.1shot** - Generic one-shot agent instructions
- **README.md** - Project overview and setup

### Code Maps (CRITICAL - Read these first!)
- **tools/INDEX.txt** - Package overview, where to find things
- **tools/csc-shared.txt** - Shared library API
- **tools/csc-server.txt** - Server implementation
- **tree.txt** - ASCII directory tree
- **p-files.list** - Flat file listing for grep

### Services & Core Logic
- **packages/csc-shared/services/agent_service.py** - Agent management
- **packages/csc-shared/services/prompts_service.py** - Workorder management
- **packages/csc-shared/api_key_manager.py** - API key rotation
- **bin/queue-worker** - Queue processor, agent spawning

### Agent Context Files (You are here!)
- **agents/<name>/context/*.md** - Agent-specific guides
- **agents/templates/default.md** - Queue ticket template

## Workflow: How Work Gets Done

1. **Workorder created** → `workorders/ready/<task>.md`
2. **User assigns** → `agent assign <task> <agent>`
   - Moves task: `ready/` → `wip/`
   - Creates ticket: `agents/<agent>/queue/in/`
3. **Queue-worker picks up** → Spawns agent with template
4. **Agent works** → Journals to `workorders/wip/<task>.md`
5. **Agent finishes** → Writes "COMPLETE" to WIP
6. **Queue-worker detects** → Commits, moves to `done/`

## Finding Things

**Need to understand a package?**
1. Read `tools/INDEX.txt` for overview
2. Read `tools/<package>.txt` for API details
3. Read the actual `.py` files

**Need to understand IRC protocol?**
- `packages/csc-shared/irc.py` - Message parsing
- `packages/csc-server/server.py` - Server core
- `packages/csc-server/server_message_handler.py` - Command handlers

**Need to understand agent system?**
- `packages/csc-shared/services/agent_service.py` - Agent CLI
- `bin/queue-worker` - Queue processing
- `agents/templates/default.md` - Task template

## Common Tasks

**Writing tests:** See `agents/<name>/context/test-guidelines.md`
**Making changes:** Journal steps to WIP before doing them
**Using code maps:** Read tools/*.txt before reading source
**Committing:** Never commit yourself - queue-worker handles it
