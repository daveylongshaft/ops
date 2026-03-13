# Improve Test Coverage and Infrastructure

**Priority**: P3 (quality)
**Estimate**: 5 hours
**Assignee**: jules | codex | gemini
**Reviewer**: anthropic (opus)

## Problem

Current test suite lacks:
- Unit test isolation (tests modify global state)
- Proper mocking (tests hit real network/filesystem)
- Fixtures for common test setup
- Coverage metrics (no visibility into untested code)

This makes tests brittle, slow, and incomplete.

## Objective

Improve test infrastructure with:
1. Test isolation using mocks for external dependencies
2. pytest fixtures for common test scenarios
3. Coverage metrics via pytest-cov
4. Standardized test patterns and helpers

## Context

**Current test issues**:
- Tests modify shared state (client_registry, channels)
- No mocking of file I/O, network, or time
- Repetitive setup code in every test
- No coverage measurement
- Tests are slow (real I/O operations)

**Test files**:
- `tests/test_server.py` - Server integration tests
- `tests/test_message_handler.py` - Message handling tests
- `tests/test_channel.py` - Channel operations tests
- Need to create more test files

## Proposed Solutions

### 1. Test Isolation with Mocking

Use `unittest.mock` to isolate tests:

```python
from unittest.mock import Mock, patch, MagicMock
import pytest

def test_handle_join_creates_channel(mock_server, mock_addr):
    """Test that JOIN creates channel if it doesn't exist."""
    handler = MessageHandler(mock_server, mock_file_handler)

    # Mock channel manager
    with patch.object(handler.server, 'channel_manager') as mock_cm:
        mock_cm.get_channel.return_value = None
        mock_cm.ensure_channel.return_value = Mock()

        msg = {'command': 'JOIN', 'params': ['#test']}
        handler._handle_join(msg, mock_addr)

        # Verify channel was created
        mock_cm.ensure_channel.assert_called_once_with('#test')
```

**Benefits**:
- Tests don't affect real state
- Fast (no real I/O)
- Predictable (no external dependencies)
- Isolated (no test interdependencies)

### 2. Pytest Fixtures

Create reusable test fixtures in `tests/conftest.py`:

```python
import pytest
from unittest.mock import Mock, MagicMock

@pytest.fixture
def mock_server():
    """Provides a mock IRC server for testing."""
    server = MagicMock()
    server.log = Mock()
    server.channel_manager = MagicMock()
    server.client_registry = {}
    server.send_message = Mock()
    return server

@pytest.fixture
def mock_file_handler():
    """Provides a mock file handler."""
    handler = MagicMock()
    handler.sessions = {}
    return handler

@pytest.fixture
def mock_addr():
    """Standard test client address."""
    return ('127.0.0.1', 12345)

@pytest.fixture
def registered_client(mock_server, mock_addr):
    """Provides a pre-registered client for testing."""
    mock_server.client_registry[mock_addr] = {
        'nick': 'testuser',
        'user': 'testuser',
        'realname': 'Test User',
        'addr': mock_addr,
        'registered': True
    }
    return mock_addr

@pytest.fixture
def test_channel(mock_server):
    """Provides a test channel with members."""
    from csc_service.shared.channel import Channel
    channel = Channel('#test')
    channel.add_member('alice', ('127.0.0.1', 10001))
    channel.add_member('bob', ('127.0.0.1', 10002))
    mock_server.channel_manager.get_channel.return_value = channel
    return channel
```

**Usage**:
```python
def test_privmsg_to_channel(mock_server, registered_client, test_channel):
    """Test sending message to channel."""
    # Test code here - all setup done by fixtures!
```

### 3. Coverage Metrics

Install and configure pytest-cov:

```bash
pip install pytest-cov
```

Add coverage config to `pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "--cov=csc_service",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=70"
]

[tool.coverage.run]
source = ["csc_service"]
omit = [
    "*/tests/*",
    "*/venv/*",
    "*/__pycache__/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

Run with coverage:
```bash
pytest --cov=csc_service --cov-report=html
```

### 4. Standardized Test Patterns

Create test helper module `tests/helpers.py`:

```python
"""Common test helpers and utilities."""

def create_irc_message(command, params=None, prefix=None):
    """Helper to create IRC message dict."""
    return {
        'command': command,
        'params': params or [],
        'prefix': prefix
    }

def assert_irc_reply(mock_send, code, contains=None):
    """Assert that IRC numeric reply was sent."""
    mock_send.assert_called()
    call_args = mock_send.call_args[0]
    assert code in str(call_args)
    if contains:
        assert contains in str(call_args)

def simulate_registration(handler, addr, nick='testuser'):
    """Simulate full client registration sequence."""
    handler.process(b'NICK ' + nick.encode(), addr)
    handler.process(b'USER testuser 0 * :Test User', addr)
    return addr
```

## Implementation Steps

1. Install test dependencies:
   ```bash
   pip install pytest pytest-cov pytest-mock
   ```

2. Create `tests/conftest.py` with fixtures (see above)

3. Create `tests/helpers.py` with test utilities

4. Refactor existing tests to use fixtures:
   - Remove manual setup code
   - Use mock fixtures instead of real objects
   - Add isolation via mocking

5. Add new test files for untested modules:
   - `tests/test_channel_manager.py` - ChannelManager tests
   - `tests/test_registration.py` - Registration flow tests
   - `tests/test_modes.py` - Mode handling tests
   - `tests/test_services.py` - Service command tests

6. Add coverage measurement to CI/CD:
   ```bash
   pytest --cov=csc_service --cov-fail-under=70
   ```

7. Generate and review coverage reports:
   ```bash
   pytest --cov=csc_service --cov-report=html
   open htmlcov/index.html
   ```

## Test Coverage Goals

Target coverage by module:

- `channel.py` - 90% (core functionality)
- `server_message_handler.py` - 80% (many handlers)
- `server.py` - 75% (network code hard to test)
- `data.py` - 85% (data persistence)
- Overall - 70% minimum

## Acceptance Criteria

- [ ] pytest-cov installed and configured
- [ ] conftest.py with core fixtures created
- [ ] helpers.py with test utilities created
- [ ] Existing tests refactored to use fixtures
- [ ] All tests use mocks for external dependencies
- [ ] Coverage report generates successfully
- [ ] Coverage above 70% overall
- [ ] Coverage reports added to CI/CD
- [ ] Documentation for writing new tests

## Files to Create

- `tests/conftest.py` - Pytest fixtures
- `tests/helpers.py` - Test utilities
- `tests/test_channel_manager.py` - New tests
- `tests/test_registration.py` - New tests
- `tests/test_modes.py` - New tests
- `pyproject.toml` - Coverage config (or update existing)

## Files to Modify

- `tests/test_server.py` - Refactor with fixtures
- `tests/test_message_handler.py` - Add mocking
- `tests/test_channel.py` - Use fixtures

## Testing the Tests

1. Run full test suite:
   ```bash
   pytest -v
   ```

2. Run with coverage:
   ```bash
   pytest --cov=csc_service --cov-report=term-missing
   ```

3. Check coverage report:
   ```bash
   pytest --cov=csc_service --cov-report=html
   firefox htmlcov/index.html
   ```

4. Verify test isolation:
   ```bash
   # Run tests in random order - all should pass
   pytest --random-order
   ```

5. Verify no side effects:
   ```bash
   # Run tests twice - results should be identical
   pytest && pytest
   ```

## Notes

- Mock external dependencies (filesystem, network, time)
- Use fixtures for common setup (reduces boilerplate)
- Aim for fast tests (entire suite <10 seconds)
- Coverage is a guide, not a goal - 100% coverage != bug-free
- Write tests for bug fixes to prevent regression
- Consider property-based testing with Hypothesis for edge cases

## Example Test Structure

```python
"""Tests for channel operations."""
import pytest
from unittest.mock import Mock, patch

def test_join_creates_channel(mock_server, mock_file_handler, registered_client):
    """Test that JOIN creates a new channel if it doesn't exist."""
    # Arrange
    handler = MessageHandler(mock_server, mock_file_handler)
    msg = create_irc_message('JOIN', ['#newchannel'])

    # Act
    handler._handle_join(msg, registered_client)

    # Assert
    mock_server.channel_manager.ensure_channel.assert_called_once_with('#newchannel')
    assert_irc_reply(mock_server.send_message, 'JOIN')

def test_join_banned_user(mock_server, mock_file_handler, registered_client, test_channel):
    """Test that banned users cannot JOIN channel."""
    # Arrange
    handler = MessageHandler(mock_server, mock_file_handler)
    test_channel.ban_list.add('testuser!*@*')
    msg = create_irc_message('JOIN', ['#test'])

    # Act
    handler._handle_join(msg, registered_client)

    # Assert
    assert_irc_reply(mock_server.send_message, 'ERR_BANNEDFROMCHAN')
```

## Coverage Report Example

```
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
csc_service/shared/channel.py            234     23    90%   45-52, 89-91
csc_service/server/server.py             189     47    75%   123-145, 234-256
csc_service/server/message_handler.py   1245    249    80%   567-589, 891-923, ...
csc_service/shared/data.py               167     25    85%   78-82, 145-149
---------------------------------------------------------------------
TOTAL                                   1835    344    81%
```
