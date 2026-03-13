---
urgency: P2
tags: testing, quality, infrastructure
---

# Comprehensive Live-System Testing Framework

## Goal

Build a testing approach that runs against the LIVE IRC server using csc-client,
testing multiple subsystems per test, with clear failure diagnostics including
context/logs from the live system.

## Current Testing Gaps

- Existing tests are unit/integration tests against mocked or localhost server
- No tests verify the full path: client -> server -> storage -> response
- No tests verify service interactions (nickserv, chanserv, botserv, oper auth)
- Test failures give stack traces but not server-side context
- No way to capture server logs alongside client-side test assertions

## Testing Improvements

### 1. Live Test Harness (csc-test-client or test mode in csc-client)

A test runner that:
- Connects to the running server as a real IRC client
- Sends IRC commands and validates responses
- Captures both client-side and server-side logs for each test
- Reports clear PASS/FAIL with full context on failure
- Can run multiple subsystem tests in sequence

### 2. Test Categories (each tests multiple subsystems)

**Connection & Auth Tests**:
- Connect, register nick, verify welcome numerics
- NickServ IDENTIFY with valid/invalid passwords
- OPER with valid/invalid credentials
- Tests: networking, user registration, nickserv, opers.json

**Channel Tests**:
- JOIN/PART channels, verify member lists
- Set/unset channel modes (+o, +v, +b, +k, +l)
- ChanServ REGISTER/INFO
- Tests: channel_manager, chanserv, mode handling, persistence

**Messaging Tests**:
- PRIVMSG to channel, verify delivery
- PRIVMSG to user (DM)
- NOTICE to channel/user
- Tests: message routing, broadcast, direct delivery

**Persistence Tests**:
- Connect, join channels, set modes, disconnect
- Reconnect, verify channels/modes survived restart
- Tests: channels.json, users.json, history.json, restore_all

**Oper Tests**:
- OPER login, verify +o mode
- KILL, KLINE, GLINE commands
- Verify protect_local_opers behavior
- Tests: opers.json, check_oper_auth, ban system

**Service Tests** (NickServ, ChanServ, BotServ):
- Full registration/identify/drop lifecycle for each
- Verify persistence across server restart
- Tests: nickserv.json, chanserv.json, botserv.json

### 3. Failure Diagnostics

Each test failure should include:
- Test name and assertion that failed
- Full IRC message exchange (sent/received)
- Server-side log excerpt (via syslog or log file) for the test window
- Relevant JSON file state (e.g., dump of channels.json after channel test fails)
- Timestamp correlation between client and server events

### 4. Implementation Approach

Option A: Python test script using raw UDP sockets (like existing tests)
Option B: Extend csc-client with a --test mode that runs test suites
Option C: Standalone test harness that imports csc_service.shared for IRC parsing

Recommended: Option C -- standalone harness that connects as a real client
but uses shared library for message parsing. Can capture server logs via
a second connection or by reading the server's log output.

### 5. Server-Side Log Capture

Add a test log channel (#test-log or similar) that the test harness JOINs.
Server broadcasts diagnostic info to this channel during tests.
Alternatively, add a TESTMODE oper command that enables verbose server logging
to a file that the test harness reads after each test.

## Deliverables

1. Test harness script (bin/live-test or similar)
2. Test suite files (one per category above)
3. Log capture mechanism (server-side)
4. Integration with existing test-runner (optional -- may want manual trigger)
5. Documentation for running live tests

## Notes

- Tests should be idempotent (clean up after themselves)
- Tests should not interfere with active users/channels
- Consider using a dedicated test nick (csc-tester) and test channel (#csc-test)
- Server must be running before tests execute (not auto-started)
