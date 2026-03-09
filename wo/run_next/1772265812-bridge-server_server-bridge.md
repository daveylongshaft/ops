# Bridge-Server Architecture Setup

## Objective
Set up encrypted local and remote CSC server/bridge infrastructure with bridge-to-bridge tunneling.

## Local Machine (Current)

### csc-server
- Listen on: `udp://0.0.0.0:9525`
- Auto-detect and enable encryption with clients that support it

### csc-bridge
Connect to local server on `udp://localhost:9525` with encryption.

Listen for incoming connections on:
- **UDP 9526** → routes to local csc-server
- **TCP 9667** → routes to local csc-server
- **TCP 9666** → forwards to remote bridge at facingaddictionwithhope.com

Auto-detect and enable encryption for all incoming connections.

## Remote Machine (facingaddictionwithhope.com)

### csc-server
- Listen on: `udp://0.0.0.0:9525`
- Auto-detect and enable encryption with clients that support it

### csc-bridge
Connect to its local server on `udp://localhost:9525` with encryption.

Listen for incoming connections on:
- **UDP 9526** → routes to remote csc-server
- **TCP 9667** → routes to remote csc-server

Auto-detect and enable encryption for all incoming connections.

## Encryption Requirements
- Server-to-Server: encrypted
- Bridge-to-Server: encrypted
- Bridge-to-Bridge: encrypted (via TCP 9666 local → TCP 9667 remote)
- Client-to-Bridge: encryption optional (on/off)
- Client-to-Server: encryption optional (on/off)

## Deployment Steps

### Step 1: Local Setup
1. Start csc-server on UDP 9525
2. Start csc-bridge with multi-port listening (9526 UDP, 9667 TCP, 9666 TCP tunneling)
3. Verify local connectivity

### Step 2: Remote Setup
1. SSH to `davey@facingaddictionwithhope.com`
2. Update repo
3. Create workorder: `/opt/csc/bin/workorders add bridge-server_server-bridge : [same instructions as this for remote side, listening on 9526 UDP and 9667 TCP only]`
4. Assign to haiku: `agent select haiku; agent assign bridge-server_server-bridge`
5. Exit and wait for completion

### Step 3: Verification
1. Test programmatic client connection to remote csc-server via local bridge TCP 9666
2. Wait 1-2 minutes for agent to complete remote setup
3. Pull repo to confirm workorder marked as complete
4. Verify remote server is online and responding

## Success Criteria
- Local csc-server listening and responding on UDP 9525
- Local csc-bridge listening and routing correctly on 9526 UDP, 9667 TCP, 9666 TCP
- Remote csc-bridge created and listening on 9526 UDP, 9667 TCP
- Successful programmatic client connection through bridge tunnel
- Both workorders marked complete in respective repos"

