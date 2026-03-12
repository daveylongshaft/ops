---
urgency: P3
---
## Service-Level Requirement: SYSTEM UP AND RUNNING

The system is ONLY considered 'up and running' when ALL of the following are TRUE:

1. **csc-ctl status** shows:
   - server: running (with port displayed)
   - bridge: running (with port displayed)

2. **Client → Bridge → Server Connectivity**:
   - Client can connect to bridge
   - Bridge can relay commands to server
   - Server responds to commands

3. **Service Module Creation & Execution**:
   - Send command to server: create new service module (class)
   - Module appears in service registry
   - Execute module via IRC: 'ai <token> <class> <method> [args]' over #general
   - Server processes and returns result

## Current Status
- Tools repaired (csc-ctl, agent, wo, sm-run)
- Services installed but not running
- Need full end-to-end integration test

## Required Tasks
1. Start server and bridge services
2. Verify ports are listening and displayed in csc-ctl status
3. Start IRC bridge
4. Connect test client
5. Create test service module via server
6. Execute test command over #general with ai token
7. Verify complete request/response cycle

When ALL three conditions above pass with working demonstration, report SYSTEM UP AND RUNNING.
