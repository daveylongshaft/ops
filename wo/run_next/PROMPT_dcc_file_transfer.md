---
requires: [python3]
platform: [windows, linux, macos]
---
# DCC SEND/GET for Service Module Exchange

## Goal
Implement DCC SEND and auto-DCC GET on all CSC clients (claude, gemini, chatgpt, dmrbot, script-runner) and the server so they can exchange service modules on-demand.

## What DCC Does Here
Standard IRC DCC SEND/GET adapted for CSC's UDP protocol:
- A client can send a file (service module `.py`) to another client
- The receiving client auto-accepts (no user confirmation needed for bots)
- Once received, the module is available for execution immediately

## Implementation

### Server Side
- Handle DCC SEND/GET routing between clients (relay the file data)
- New handler methods in `server_message_handler.py` for DCC protocol
- File data transmitted as base64-encoded chunks over existing UDP transport
- Max file size limit (configurable, default 1MB for service modules)

### Client Side (all AI clients + script-runner)
- Auto-accept incoming DCC transfers
- Save received `.py` files to local `services/` directory
- Reload service registry after receiving a new module
- Support sending: `DCC SEND <nick> <filepath>`

### Protocol
```
# Sender initiates
PRIVMSG <target> :\x01DCC SEND <filename> <filesize>\x01
# Followed by data chunks
PRIVMSG <target> :\x01DCC DATA <filename> <chunk_num> <base64_data>\x01
# End marker
PRIVMSG <target> :\x01DCC EOF <filename> <checksum>\x01

# Receiver confirms
PRIVMSG <sender> :\x01DCC ACK <filename>\x01
```

### Integration with Service System
- Received modules go into the client's `services/` directory
- Client's service loader picks them up on next command
- Enables on-the-fly capability sharing between agents

## Verification
- Client A sends `builtin_service.py` to Client B via DCC
- Client B receives it, loads it, can now run builtin commands
- Verify checksum matches after transfer

PID: 37328 agent: gemini-3-pro starting at 2026-02-22 10:32:41

PID: 28588 agent: gemini-3-pro starting at 2026-02-22 10:35:21

PID: 9096 agent: haiku starting at 2026-02-22 10:35:47

PID: 38316 agent: gemini-2.5-flash starting at 2026-02-22 10:37:38

PID: 22596 agent: gemini-2.5-flash starting at 2026-02-22 10:38:55

PID: 30172 agent: gemini-2.5-flash starting at 2026-02-22 10:39:40

PID: 32120 agent: gemini-2.5-flash-lite starting at 2026-02-22 10:40:10

PID: 32612 agent: qwen starting at 2026-02-22 10:46:15

PID: 35688 agent: qwen starting at 2026-02-22 10:49:35

PID: 33308 agent: qwen starting at 2026-02-22 10:56:17

PID: 12308 agent: qwen starting at 2026-02-22 10:57:36

## Completion Log (agent update)
- Implemented client-side CTCP DCC SEND support in shared CSC client base.
- Added `/dcc send <nick> <pathspec>` command with glob/pathspec expansion.
- Added automatic handling of inbound CTCP `DCC SEND` offers and auto-receive to `run/downloads/`.
- Added sender/receiver transfer workers with mIRC-style cumulative 32-bit ACK behavior.
- Fixed sender-side ACK read loop to avoid receiver-side connection reset during ACK emission.
- Confirmed Gemini client imports shared `csc_service.client.client.Client` base.
- Added/rewrote `tests/test_dcc_system.py` with:
  - localhost end-to-end DCC transfer regression test,
  - `/dcc` usage diagnostic test,
  - Gemini import regression test.
- Updated `docs/client.md` with a full DCC feature section, behavior notes, and command examples.
- Updated root `README.md` documentation index to link DCC transfer documentation.
- Appended contribution credit in `contrib.txt`.
- Added `/dcc ports <low[-high]>` command to configure DCC listener port behavior.
- Implemented persistent DCC port storage via Data object keys `dcc_port_low` and `dcc_port_high`.
- Implemented listener allocation logic to honor fixed port or inclusive configured range during DCC SEND offers.
- Added tests for DCC port command persistence and invalid range diagnostics in `tests/test_dcc_system.py`.
- Updated `docs/client.md` with `/dcc ports` behavior, persistence note, and command examples.
- Added auto reverse-connect fallback flow when initial DCC connect-back fails (firewall/NAT scenario).
- Added CTCP `DCC REVERSE` control message handling to coordinate fallback direction automatically.
- Added regression test covering connect-back failure followed by successful reverse fallback transfer.
- Updated docs with reverse fallback behavior notes and example guidance.
COMPLETE
