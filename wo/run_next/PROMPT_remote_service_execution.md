---
requires: [python3]
platform: [windows, linux, macos]
---
# Remote Service Module Execution via IRC

## Goal
Allow any CSC client to execute service module methods on any other connected client, using the existing AI token command protocol over IRC.

## How It Works

### Remote Command Execution
Any client can send a command to another client's service layer:
```
PRIVMSG gemini :gemini <token> <service_class> <method> [args...]
```
Example:
```
PRIVMSG gemini :gemini do builtin list_dir /opt/csc
```
Gemini's client receives this, routes it through its local `service.py` handler, runs `builtin.list_dir("/opt/csc")`, and sends the result back as a PRIVMSG.

### Remote Module Upload
Upload a service module to a remote client inline:
```
PRIVMSG gemini :<begin file=newspaper_service.py>
PRIVMSG gemini :import requests
PRIVMSG gemini :class newspaper:
PRIVMSG gemini :    def headlines(self):
PRIVMSG gemini :        return "Top stories..."
PRIVMSG gemini :<end file>
```
The receiving client:
1. Buffers lines between `<begin file=X>` and `<end file>`
2. Writes the file to its local `services/` directory
3. Responds with confirmation: "Loaded newspaper_service.py (4 lines)"
4. Module is now available for remote command execution

## Implementation

### Client Side Changes (all AI clients)
- Add a service command dispatcher to the client's message handler
- When a PRIVMSG matches the token command pattern, route to local service.py
- Return results as PRIVMSG back to sender
- Add `<begin file>` / `<end file>` parser for inline module uploads
- Save uploaded modules to client's local `services/` directory

### Server Side
- No changes needed - this uses existing PRIVMSG routing
- Server just relays messages between clients as normal

### Security
- Only accept commands from authenticated IRC users (registered nicks)
- Token validation required (existing AI token system)
- File uploads restricted to `*_service.py` naming pattern
- Max upload size limit

## Verification
1. Start server, claude client, gemini client
2. From claude: `PRIVMSG gemini :gemini do version get`
3. Gemini should respond with its version info
4. Upload a test service module to gemini via `<begin file>...<end file>`
5. Execute the uploaded module's method remotely
