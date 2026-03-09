# Prompt: Docstrings — Test Files

## Goal

Add docstrings to all undocumented test helpers, setUp/tearDown methods, and utility functions in `/opt/csc/tests/`. These don't need the full "What calls it / What it calls" convention — test docstrings should be brief and practical.

## Docstring Standard for Tests

**Same bar as production code: you should be able to understand what a test does, what it needs, and what it proves without reading the test body.**

**Why:** These docstrings are interface contracts, not implementation notes. Any function should be re-implementable in any language or logic model and the system still works — as long as the contract is honored. Document the *what*, not the *how*. For tests specifically: the docstring defines what behavior is guaranteed, so a reimplementation in another language knows exactly what to verify.

**Logic tables:** If a test helper or fixture maps finite inputs to outputs (e.g. command → expected numeric, mode → expected permission), document the full mapping. An implementer should be able to build a lookup table from the docstring alone.

For test helpers and fixtures, include:

1. **Args** — every argument: name, type, valid values.
2. **Returns** — exact return type and what's in it.
3. **Data** — what fixtures, mocks, or state it creates. For setUp, document every self.* attribute it creates and their types/shapes.
4. **Side effects** — temp files, sockets opened, processes spawned.
5. **Children** — helper functions it calls (if non-obvious).

For test methods (test_*), include:

1. **What it tests** — the specific behavior being verified.
2. **Setup** — any preconditions beyond what setUp provides.
3. **Assertions** — what it asserts and the expected values.

```python
def setUp(self):
    """Set up test fixtures for persistence tests.

    Data:
        self.tmp_dir (str): Temp directory path, created via tempfile.mkdtemp().
        self.server (Server): Mock server with storage at self.tmp_dir.
            Has empty channels, users, opers dicts.
        self.handler (ServerMessageHandler): Attached to self.server.
        self.addr (tuple[str, int]): Fake client address ("127.0.0.1", 9999).

    Side effects:
        Creates a temp directory on disk. Cleaned up in tearDown().

    Children:
        _build_server(self.tmp_dir)
    """

def _build_server(tmp_dir):
    """Build a Server instance with storage pointed at a temp directory.

    Args:
        tmp_dir (str): Path to existing temp directory for JSON storage.
            Must exist and be writable.

    Returns:
        Server: Configured instance with empty state dicts, socket not bound,
            not yet running. Storage files will be created on first write.

    Children:
        Server.__init__(), StorageManager.__init__()
    """

def send_irc(sock, line):
    """Send a raw IRC line to the given socket, appending CRLF.

    Args:
        sock (socket.socket): Connected UDP or TCP socket.
        line (str): IRC command without trailing CRLF (e.g. "NICK alice").

    Returns:
        None

    Side effects:
        Sends (line + "\\r\\n").encode() over the socket.
    """

def test_away_set(self):
    """Verify AWAY with a message sets the user as away.

    Setup:
        Requires a registered, connected client at self.addr.

    Assertions:
        Server responds with RPL_NOWAWAY (306).
        self.server.users[nick].away is set to the provided message string.
    """
```

**Omit sections only if truly not applicable.** When in doubt, include it.

## Items to Document (56 items across test files)

### tests/test_complete_persistence.py
- `_build_server` (line 21), `_register` (line 51), `_restart` (line 57)
- `TestCompletePersistence.setUp` (line 66), `tearDown` (line 69)

### tests/test_gemini.py
- `DataHarness.__init__` (line 10), `get_data` (line 12), `put_data` (line 14)
- `TestGemini.setUp` (line 19)

### tests/test_handler_persistence.py
- `_build_mock_server` (line 22), `_register_client` (line 50)
- `TestHandlerPersistence.setUp` (line 63)

### tests/test_nickserv_ghost.py
- `TestNickServGhost.setUp` (line 102)

### tests/test_nickserv_registration.py
- `TestNickServRegistration.setUp` (line 101)

### tests/test_power_failure_resilience.py
- `TestPowerFailure.setUp` (line 77), `tearDown` (line 82)

### tests/test_stale_nick_cleanup.py
- `TestStaleNickCleanup.setUp` (line 100)

### tests/test_storage_manager.py
- `TestAtomicIO.setUp` (line 18), `tearDown` (line 25)
- `TestChannelOperations.setUp` (line 85), `tearDown` (line 92)
- `TestHistoryOperations.setUp` (line 175), `tearDown` (line 182)
- `TestOperOperations.setUp` (line 217), `tearDown` (line 224)
- `TestBanOperations.setUp` (line 244), `tearDown` (line 251)

### tests/test_topic_command.py
- `TestTopicCommand.setUp` (line 18)

### tests/test_user_mode_away.py
- `send_irc` (line 7), `recv_all_irc` (line 11), `create_client` (line 26)
- `test_away_set` (line 35), `test_away_unset` (line 56)
- `test_whois_shows_away` (line 79), `test_cannot_set_a_via_mode` (line 97)

### tests/test_user_mode_invisible.py
- `send_irc` (line 7), `create_client` (line 27)
- `test_set_invisible` (line 38), `test_remove_invisible` (line 50)
- `test_query_modes` (line 64), `test_usersdontmatch` (line 78)
- `test_unknown_flag` (line 92), `test_combined_modes` (line 104)

### tests/test_user_mode_operator.py
- `send_irc` (line 7)

### tests/test_user_mode_server_notices.py
- `send_irc` (line 7), `recv_all_irc` (line 11), `create_client` (line 26)
- `test_set_server_notices` (line 35), `test_remove_server_notices` (line 47)
- `test_combined_with_s` (line 61)

### tests/test_user_mode_wallops.py
- `send_irc` (line 7), `recv_all_irc` (line 11), `create_client` (line 26)
- `test_set_wallops` (line 35), `test_remove_wallops` (line 47)
- `test_combined_with_w` (line 61)

## Rules

- Do NOT change any test logic — docstrings only
- Read each file before editing
- Use Haiku-tier agents — this is repetitive work
- After finishing, run: `python3 /opt/csc/analyze_project.py` and verify 0 undocumented items in `analysis_report.json`

Verified complete.
