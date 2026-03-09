---
requires: [python3, git, ntplib]
platform: [windows, linux]
agent: haiku
---

# Time Synchronization for Server Merges & Nick Collisions

## Objective

Implement time synchronization verification for CSC servers to ensure accurate nick collision resolution when servers merge into a federated network.

## Background

When two CSC servers link together, they may find users with the same nickname. To resolve collisions fairly, we need:
1. **Reliable timestamp** when user connected to original server
2. **Time drift detection** between servers
3. **NTP verification** for system clock accuracy

## Implementation

### 1. Server Startup Timestamp

**File: `packages/csc-server/server.py`**

Add to `Server.__init__()`:
```python
import time
from pathlib import Path

self.startup_time = time.time()  # Unix timestamp
self.startup_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.startup_time))

# Persist to file for recovery
self.startup_file = Path("server_startup_time.json")
self._save_startup_time()

def _save_startup_time(self):
    """Save server startup time atomically."""
    data = {
        "startup_time": self.startup_time,
        "startup_time_str": self.startup_time_str,
        "server_id": os.getenv("CSC_SERVER_ID", "unknown")
    }
    # Atomic write pattern
    import json, tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(data, f)
        temp_path = f.name
    Path(temp_path).replace(self.startup_file)
    self.log(f"Startup time persisted: {self.startup_time_str}")
```

### 2. User Connection Timestamp

**File: `packages/csc-server/server.py`**

Track when each user connected:
```python
def handle_user_connect(self, nick, addr):
    """Track user connection time for collision resolution."""
    connect_time = time.time()

    # Store in users dict
    if nick not in self.clients:
        self.clients[nick] = {
            "addr": addr,
            "connect_time": connect_time,
            "modes": set(),
            "channels": set()
        }
    self.log(f"User {nick} connected at {time.strftime('%H:%M:%S', time.localtime(connect_time))}")
```

### 3. NTP Time Verification

**File: `packages/csc-shared/time_sync.py`** (new)

```python
"""NTP time synchronization verification."""

import socket
import struct
import time
from typing import Tuple, Optional

class NTPClient:
    """Simple NTP client for time verification."""

    def __init__(self, server: str = "pool.ntp.org", timeout: int = 3):
        self.server = server
        self.timeout = timeout

    def get_ntp_time(self) -> Optional[float]:
        """
        Get current time from NTP server.

        Returns:
            Unix timestamp from NTP server, or None if failed
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)

            # NTP request packet
            ntp_query = b'\x1b' + 47 * b'\0'
            sock.sendto(ntp_query, (self.server, 123))

            # Receive response
            response, _ = sock.recvfrom(1024)
            sock.close()

            # Extract timestamp (seconds since 1900-01-01)
            ntp_time = struct.unpack('!12I', response)[10]

            # Convert to Unix timestamp (1970-01-01)
            return ntp_time - 2208988800

        except Exception as e:
            return None

    def check_time_drift(self) -> Tuple[bool, float]:
        """
        Check if system time is in sync with NTP server.

        Returns:
            (is_synced: bool, drift_seconds: float)
            - is_synced: True if drift < 10 seconds
            - drift_seconds: Absolute difference from NTP time
        """
        ntp_time = self.get_ntp_time()
        if ntp_time is None:
            return None, None  # NTP check failed

        local_time = time.time()
        drift = abs(ntp_time - local_time)

        return drift < 10.0, drift
```

### 4. Server S2S Time Exchange

**For opus's server linking prompt:**
When two servers establish an S2S link:

```python
# In ServerLink.authenticate():
def exchange_timestamps(self):
    """Exchange server startup times during handshake."""
    msg = f"SLINKTIME {self.local_server.startup_time} {self.local_server.server_id}"
    self.send_message(msg)

    # Receive remote timestamp
    response = self.receive_message()
    if response.startswith("SLINKTIME"):
        parts = response.split()
        remote_time = float(parts[1])
        remote_id = parts[2]

        time_drift = abs(self.local_server.startup_time - remote_time)
        if time_drift > 10.0:
            self.log(f"WARNING: Time drift {time_drift}s with {remote_id}")
            # Continue anyway, but log warning
```

### 5. Configuration

**Update `.env`:**
```env
CSC_SERVER_ID=server_001
CSC_NTP_SERVER=pool.ntp.org
CSC_TIME_DRIFT_TOLERANCE=10  # seconds
```

### 6. Platform Integration

The platform layer already detects NTP sync status in `platform.json`:
```json
{
  "time": {
    "ntp_synced": true,
    "clock_warning": null
  }
}
```

Ensure this is checked on startup and logged.

## Testing

1. **Verify server tracks connection times:**
   ```bash
   grep "connect_time\|connected at" server.log
   ```

2. **Verify NTP check runs:**
   ```bash
   grep "NTP\|time drift\|synced" server.log
   ```

3. **Verify timestamps persist:**
   ```bash
   cat server_startup_time.json
   ```

## Deliverables

- [ ] Server tracks `startup_time` on init
- [ ] Server tracks `connect_time` for each user
- [ ] `NTPClient` class created in csc-shared
- [ ] S2S handshake includes time exchange (work with opus on this)
- [ ] Platform.json NTP status is logged
- [ ] Tests verify time tracking works correctly
- [ ] Commit: "Add time synchronization for server merges"

## Files to Modify

1. `packages/csc-server/server.py` — Add startup_time and user connect_time
2. `packages/csc-shared/time_sync.py` — New NTP client (create)
3. `.env` — Add CSC_SERVER_ID, CSC_NTP_SERVER
4. Tests: `tests/test_time_sync.py` — Test NTP client and time tracking

## Notes

- NTP library: Use stdlib socket/struct (no new dependencies)
- Fallback: If NTP unavailable, use system time
- Thread-safe: Time tracking uses existing locks from Data class
- No breaking changes to existing IRC functionality
--- RESTART Thu, Feb 19, 2026  1:41:35 PM ---
AGENT_PID: 1004
