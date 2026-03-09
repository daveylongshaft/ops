# Document BotServ and ChanServ Services

## Context
Two new IRC services have been implemented in the CSC system:
- **BotServ**: Channel bot registration and management service
- **ChanServ**: Channel registration and access control service

Both services are located at:
- `/opt/csc/packages/csc_shared/services/botserv_service.py`
- `/opt/csc/packages/csc_shared/services/chanserv_service.py`

## Task
Write comprehensive documentation for these two services that will be added to the README.md file.

The documentation should cover:

### 1. Service Overview
- Brief description of what each service does
- Primary use cases
- Integration points with the IRC server

### 2. Command Reference
For **BotServ**:
- ADD <botnick> <#chan> <password> - Register a bot for a channel
- DEL <botnick> <#chan> - Unregister a bot
- LIST [#chan] - List registered bots

For **ChanServ**:
- REGISTER <#chan> <topic> - Register a channel
- OP <#chan> <nick> - Add a nick to the oplist
- DEOP <#chan> <nick> - Remove a nick from the oplist
- VOICE <#chan> <nick> - Add a nick to the voicelist
- DEVOICE <#chan> <nick> - Remove a nick from the voicelist
- BAN <#chan> <mask> - Add a mask to the banlist
- UNBAN <#chan> <mask> - Remove a mask from the banlist
- LIST - List registered channels
- INFO <#chan> - Show registration info

### 3. Data Storage
- Explain how state is persisted (botserv.json and chanserv.json via PersistentStorageManager)
- Data structure and schema
- Recovery behavior on server restart

### 4. Features & Implementation Notes
- BotServ: Bot lifecycle management, channel association, password protection
- ChanServ: Topic persistence, operator/voice management, ban enforcement, state application on channel join

### 5. Usage Examples
Provide IRC command examples showing:
- How users register bots with BotServ
- How users register channels and manage access with ChanServ
- How modes and bans are enforced

### 6. API/Integration Details
- How the services integrate with the IRC message handler
- How ChanServ's `apply_channel_state()` is called by the server
- Service lifecycle and initialization

## Code References
The services are referenced in the codebase tools index:
```
tools/services.txt  (15 files, 15 classes, 108 funcs)
```

Read the botserv_service.py and chanserv_service.py files for implementation details.

## Output
Write the documentation in markdown format. It should be suitable for inclusion in the main README.md or a dedicated SERVICES.md file. Format should follow the existing project documentation style.

## Do NOT:
- Modify the service implementations themselves
- Create separate service files
- Add features beyond what's currently implemented
- Include authentication details or passwords in examples
