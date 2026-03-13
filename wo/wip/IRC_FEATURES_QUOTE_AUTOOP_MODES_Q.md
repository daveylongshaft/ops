# Workorder: Client /quote /raw, Channel Founder Auto-Op, Mode Enforcement, Silent Join/Part, Clean Restart

**Status**: IN PROGRESS
**Created**: 2026-03-13
**Priority**: P1

## Phases

### Phase 1: Add /quote, /raw commands to client [DONE]
- File: clients/client/client.py
- Add /quote and /raw as explicit commands before the else fallback
- Update help text

### Phase 2: Auto-Op Channel Founder [DONE]
- File: server/server_message_handler.py
- First joiner of empty channel gets +o and channel gets +nt
- Insert before ChanServ block in _handle_join()

### Phase 3: Tighten User Mode Enforcement [DONE]
- File: server/server_message_handler.py
- Opers can only set +o/-o on other users, not +i/+w/+s
- Modify _handle_user_mode()

### Phase 4: Silent Join/Part (+Q channel mode) [DONE]
- File: server/server_message_handler.py
- Add Q to _FLAG_MODES
- In _handle_join() broadcast: if +Q, only send JOIN to joiner
- In _handle_part() broadcast: if +Q, only send PART to parting user

### Phase 0: Clean Restart [PENDING - RUNS AFTER 1-4]
- touch SHUTDOWN, wait, csc-ctl remove all
- git commit+push all repos
- pip reinstall, rm SHUTDOWN, csc-ctl install all

### Phase 5: Comprehensive Testing [PENDING - RUNS AFTER 0]
- Test all IRC commands interactively

## Progress Log
