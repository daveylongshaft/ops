# CSCS Encryption Implementation — Complete Specification & Context

## Executive Summary

Implement automatic encryption negotiation for all CSC (Competitive Secure Communication) protocol messages. The system should auto-detect capability, negotiate encryption keys via Diffie-Hellman, encrypt payload with AES-256-GCM, and gracefully fall back to plaintext if encryption negotiation fails.

**Target:** All CSC traffic (server↔client, client↔client DCC, bridge relaying) should support transparent encryption without configuration.

---

## Protocol Specification (From docs/library/protocol.md)

### CSC (Competitive Secure Communication) — Native UDP Protocol

CSC is **not IRC**. It uses RFC 2812 message format over UDP, requiring a bridge to talk to actual IRC.

### CSCS — Encrypted CSC

**Encryption Method: AES-256-GCM with Diffie-Hellman Key Exchange**

#### Diffie-Hellman Phase

1. **Server → Client:**
   ```
   CRYPTOINIT DH <p> <g> <server_public_key>
   ```
   - `p`: RFC 3526 Group 14 prime (2048-bit MODP)
   - `g`: Generator (2 for Group 14)
   - `server_public_key`: Server's DH public value

2. **Client → Server:**
   ```
   CRYPTOINIT DHREPLY <client_public_key>
   ```

3. **Both sides:** Compute shared secret via standard DH: `shared_secret = (peer_public_key ^ private_key) mod p`

#### AES-256-GCM Encryption Phase

**Per-message encryption after DH succeeds:**
- **IV:** 12 random bytes (different per message)
- **Key:** 32 bytes derived from shared secret (via HKDF or simple hash)
- **Cipher:** AES-256 in GCM mode
- **Auth Tag:** 16 bytes (GCM-generated, verified on decrypt)
- **Wire Format:** `IV (12 bytes) || Ciphertext || Auth Tag (16 bytes)`

#### Auto-Detection

- **`is_encrypted()` function:** Uses UTF-8 decode heuristic to distinguish plaintext IRC/CSC from binary encrypted blocks
- If first 12 bytes + ciphertext + tag don't decode as valid UTF-8 → encrypted
- If decodes as UTF-8 → plaintext CSC

---

## Codebase Structure

### Current Layout

```
/c/csc/
├── irc/                                    # Code directory
│   ├── packages/csc-service/               # Main unified service package
│   │   └── csc_service/
│   │       ├── main.py                     # Service entry point
│   │       ├── shared/
│   │       │   └── platform.py             # Platform detection
│   │       └── infra/
│   │           └── pr_review.py            # PR review service
│   └── CLAUDE.md                           # Project instructions
├── ops/
│   └── wo/                                 # Workorders (formerly prompts)
│       ├── ready/
│       ├── wip/
│       ├── done/
│       └── hold/
├── agents/                                 # Running agents with queues
├── docs/
│   ├── library/
│   │   ├── protocol.md                     # CSC/CSCS protocol spec (source of truth)
│   │   ├── services.md
│   │   ├── client.md
│   │   └── server.md
│   └── tools/
│       └── INDEX.txt                       # Code map index
└── tools/
    ├── csc-service.txt                     # Code map for csc-service package
    ├── root.txt                            # Root-level code map
    └── .lastrun                            # Timestamp of last refresh-maps
```

### Code Maps Available

**For this work, consult:**
- `tools/csc-service.txt` — Classes/methods in csc-service package (1068 functions, 84 classes)
- `docs/library/protocol.md` — Full CSC/CSCS protocol specification
- `irc/CLAUDE.md` — Project conventions and architecture

### Current csc-service Package Structure

```
csc_service/
├── main.py                     # Service daemon entry, polling loop
├── __init__.py
├── shared/
│   ├── __init__.py
│   ├── platform.py             # Platform detection (hardware, OS, Docker, AI agents)
│   └── [OTHER SHARED MODULES]
├── infra/
│   ├── __init__.py
│   ├── pr_review.py            # PR review automation
│   ├── queue_worker.py         # Queue processing (if it exists)
│   ├── pm.py                   # Project manager (if it exists)
│   └── [OTHER INFRA MODULES]
├── clients/                    # AI clients (Claude, Gemini, ChatGPT)
├── server/                     # IRC/CSC server implementation
└── bridge/                     # Protocol bridge (CSC ↔ IRC translation)
```

---

## What Needs to Be Implemented

### 1. **Network Communication Layer** (NEW MODULE)

**Location:** `csc_service/shared/network.py` (or `csc_service/network.py`)

**Purpose:** Handle all UDP socket I/O with transparent encryption/decryption.

**Must Provide:**

```python
class Network:
    """UDP socket handler with transparent CSCS encryption."""

    def __init__(self, host='127.0.0.1', port=9525):
        """Initialize UDP socket."""
        pass

    def send(self, addr, data: str, encrypt=True) -> bool:
        """Send CSC message (auto-encrypt if negotiate succeeded)."""
        pass

    def recv(self, timeout=1.0) -> tuple[addr, str]:
        """Receive CSC message (auto-decrypt if CSCS connection)."""
        pass

    def initiate_encryption(self, peer_addr) -> bool:
        """Server: Send CRYPTOINIT DH, expect DHREPLY."""
        pass

    def respond_encryption(self, peer_addr, server_dh_params) -> bool:
        """Client: Parse CRYPTOINIT DH, send DHREPLY, derive secret."""
        pass

    def is_encrypted(self, data: bytes) -> bool:
        """Heuristic: UTF-8 decode → plaintext, binary → encrypted."""
        pass
```

**Internal State (per peer address):**
```python
# Track encryption status per connection
_encryption_state: Dict[addr, {
    'mode': 'plaintext' | 'encrypted',
    'shared_secret': bytes | None,
    'dh_private_key': int | None,
    'negotiation_pending': bool,
}]
```

### 2. **Diffie-Hellman Module**

**Location:** `csc_service/shared/dh.py` or part of `network.py`

**Must Provide:**

```python
# RFC 3526 Group 14 constants
RFC3526_GROUP14_PRIME = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE65381FFFFFFFFFFFFFFFF
RFC3526_GROUP14_GENERATOR = 2

def dh_generate_keypair() -> tuple[int, int]:
    """Generate random private key and compute public key."""
    private_key = secrets.randbelow(RFC3526_GROUP14_PRIME - 2) + 1
    public_key = pow(RFC3526_GROUP14_GENERATOR, private_key, RFC3526_GROUP14_PRIME)
    return private_key, public_key

def dh_compute_shared_secret(peer_public_key: int, own_private_key: int) -> bytes:
    """Compute shared secret, convert to 32-byte key."""
    shared = pow(peer_public_key, own_private_key, RFC3526_GROUP14_PRIME)
    return shared.to_bytes(256, 'big')[:32]  # Extract 32 bytes
```

### 3. **AES-256-GCM Encryption Module**

**Location:** Part of `network.py` or `csc_service/shared/crypto.py`

**Must Provide:**

```python
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_message(plaintext: str, key: bytes) -> bytes:
    """Encrypt CSC message with AES-256-GCM.

    Returns: IV (12) || Ciphertext || Tag (16)
    """
    iv = os.urandom(12)
    cipher = AESGCM(key)
    ciphertext = cipher.encrypt(iv, plaintext.encode('utf-8'), None)
    return iv + ciphertext  # Tag appended by AESGCM

def decrypt_message(encrypted: bytes, key: bytes) -> str:
    """Decrypt CSCS message.

    Raises: cryptography.exceptions.InvalidTag on auth failure
    """
    iv = encrypted[:12]
    ciphertext_and_tag = encrypted[12:]
    cipher = AESGCM(key)
    plaintext = cipher.decrypt(iv, ciphertext_and_tag, None)
    return plaintext.decode('utf-8')
```

**NOTE:** `cryptography` library uses stdlib under the hood. If banned, implement AES-256-GCM via `Crypto.Cipher.AES` from PyCryptodome or hand-rolled (not recommended).

### 4. **Integration Points**

#### Server (main.py or server.py)

```python
# On new client connection:
network.initiate_encryption(client_addr)  # Send CRYPTOINIT DH

# On receive CRYPTOINIT DHREPLY:
network.respond_encryption(client_addr, reply_data)  # Derive shared secret, enable encryption

# Timeout (5s no DHREPLY):
# Continue with plaintext (graceful fallback)

# Send/receive messages:
network.send(client_addr, message)  # Auto-encrypts if CSCS active
network.recv()  # Auto-decrypts if CSCS active
```

#### Client (client.py or in csc-client package)

```python
# On connect to server:
# Wait for CRYPTOINIT DH from server
dh_params = network.recv()  # Parse server's DH offer

# Respond:
network.respond_encryption(server_addr, dh_params)  # Send DHREPLY, derive secret

# Subsequent send/recv:
network.send(server_addr, message)  # Auto-encrypted
network.recv()  # Auto-decrypted
```

#### DCC (Direct Client Connection)

```python
# Sender → Receiver (after TCP socket opens):
sender.network.initiate_encryption(receiver_addr)

# Receiver:
# Parse CRYPTOINIT DH, send DHREPLY

# File transfer / CHAT payload:
# All subsequent data encrypted
```

#### Bridge

```python
# Bridge receives encrypted CSC from client:
encrypted_data = cscs_socket.recv()

# Bridge relays to server as-is (doesn't re-encrypt):
server_socket.send(encrypted_data)

# Bridge receives encrypted CSC from server:
# Relay to client as-is

# Bridge translates CSC → IRC (for external IRC clients):
csc_message = network.recv()  # Auto-decrypted by Network class
irc_message = bridge.translate_to_irc(csc_message)
irc_client_socket.send(irc_message)
# (No re-encryption; IRC is plaintext)
```

---

## Implementation Notes

### Key Design Decisions (For Your Judgment)

1. **Network Class Location:**
   - Option A: `csc_service/shared/network.py` (shared by all components)
   - Option B: `csc_service/network.py` (top-level service module)
   - **Jules decides:** Where makes most sense given existing patterns.

2. **Encryption Key Derivation:**
   - Simple: `key = shared_secret[:32]`
   - Robust: `key = HKDF(shared_secret, info=b'CSCS', length=32)` (using `hashlib`)
   - **Jules decides:** Based on security posture desired.

3. **Timeout for CRYPTOINIT:**
   - Default: 5 seconds (clients slow to respond)
   - Tunable: Via `Network.__init__(dh_timeout=5.0)`
   - **Jules decides:** Reasonable default.

4. **Fallback Behavior on Encryption Failure:**
   - Option A: Silently continue plaintext (transparent)
   - Option B: Log warning, continue plaintext
   - Option C: Reject connection (hard fail)
   - **Jules decides:** Based on network resilience goals.

5. **Per-Connection State Storage:**
   - Option A: Dict keyed by `(host, port)` tuple
   - Option B: Object-oriented (NetworkConnection per peer)
   - Option C: Thread-local storage (if multi-threaded)
   - **Jules decides:** Based on concurrency model.

### Coding Standards & Conventions

**You must follow CSC project patterns exactly:**

1. **File Organization: One Class Per File**
   - Each class in its own `.py` file
   - Class name derived from filename:
     - `network.py` → `class Network`
     - `dh.py` → `class DH` (or `class DiffieHellman`)
     - `crypto.py` → `class Crypto` (or split into multiple files if multiple classes)
   - If you need multiple classes, create multiple files
   - Example structure:
     ```
     csc_service/shared/
     ├── network.py          # class Network
     ├── dh.py               # class DH
     ├── aes_gcm.py          # class AESGCM
     └── encryption.py       # class Encryption (if coordination needed)
     ```

2. **Path Handling: Use Platform() Class**
   - **ALL paths** must use `Platform()` for resolution
   - Never hardcode paths like `/c/csc/` or `/home/user/`
   - Pattern:
     ```python
     from csc_service.shared.platform import Platform

     class Network:
         def __init__(self):
             self.plat = Platform()
             self.log_path = self.plat.get_abs_root_path(['logs', 'network.log'])
             self.config_path = self.plat.get_abs_root_path(['config', 'network.json'])
     ```
   - Reason: Cross-platform support (Windows/Linux/Cygwin)

3. **Class Inheritance Chain**
   - Follow the project's inheritance hierarchy:
     ```
     Root → Log → Data → Version → Platform → Network → [Your Class]
     ```
   - At minimum, inherit from `Log` or `Data` (depending on whether you need logging/persistence)
   - Check existing patterns in `tools/csc-service.txt` to see what classes inherit from

4. **Logging & Error Handling**
   - Use `self.log()` for all logging (inherited from Log class)
   - Log levels: `self.log(msg, "INFO"|"WARN"|"ERROR"|"DEBUG")`
   - Example:
     ```python
     def initiate_encryption(self, addr):
         self.log(f"Starting DH negotiation with {addr}", "INFO")
         try:
             # ... DH logic
             self.log(f"DH success with {addr}", "INFO")
         except Exception as e:
             self.log(f"DH failed: {e}", "ERROR")
             return False
     ```

5. **State Persistence**
   - If Network needs to persist encryption state, inherit from `Data`
   - Store state in JSON via `self.store('key', value)` / `self.load('key')`
   - State files live in `tmp/csc/run/` (managed by Data class)
   - Example:
     ```python
     class Network(Data):
         def save_encryption_state(self, addr, secret):
             self.store(f'encryption_{addr}', {'secret': secret.hex()})
     ```

6. **Module Imports**
   - Import from `csc_service.shared.*` not relative imports
   - Example:
     ```python
     from csc_service.shared.platform import Platform
     from csc_service.shared.log import Log
     from csc_service.shared.data import Data
     ```

7. **Type Hints**
   - Use Python 3.8+ type hints:
     ```python
     def encrypt_message(self, plaintext: str, key: bytes) -> bytes:
         pass

     def get_peer_state(self, addr: tuple[str, int]) -> dict | None:
         pass
     ```

8. **Docstrings**
   - Module-level docstring explaining purpose
   - Class-level docstring
   - Method docstrings for public API
   - Example:
     ```python
     """
     network.py - UDP socket handler with CSCS encryption.

     Provides: automatic DH negotiation, AES-256-GCM encryption/decryption,
     transparent fallback to plaintext if encryption fails.
     """

     class Network(Log):
         """UDP socket handler with transparent CSCS encryption."""

         def initiate_encryption(self, peer_addr: tuple[str, int]) -> bool:
             """Server-side: initiate DH handshake with peer.

             Returns: True if DH negotiation succeeded, False on timeout/error.
             """
     ```

9. **Testing Location**
   - Tests go in `tests/test_network.py`, `tests/test_dh.py`, etc.
   - Follow existing test patterns (check `tools/tests.txt`)
   - Use pytest conventions

10. **Configuration**
    - If Network needs config, add to `csc-service.json` or per-module JSON in `tmp/csc/config/`
    - Use Platform() to locate config files
    - Parse at initialization, validate with sensible defaults

---

### Feature Stability & Backward Compatibility

**Critical Constraint: Do NOT break existing functionality**

1. **All Existing CSC Traffic Must Continue Working**
   - Plaintext CSC clients must connect successfully (fallback mechanism)
   - Server must remain responsive to plaintext PRIVMSG, JOIN, PART, etc.
   - No existing tests should fail after your commit
   - Bridge must continue relaying traffic (encrypted or plaintext)

2. **Verify No Regressions**
   - Before committing: run full test suite locally
   - All tests in `tests/` must pass
   - New CSCS code must not interfere with non-encrypted channels
   - DCC (if existing) must work with and without encryption

3. **Integration Without Breaking**
   - Network() is a new addition; don't modify existing network code unless necessary
   - If you must modify existing classes (Server, Client, Bridge), do so minimally
   - Add new methods; don't change signatures of existing methods
   - If you add dependencies to existing classes, ensure they gracefully handle encryption absence

---

### Documentation Requirements

**Update docs without removing anything; append only.**

1. **Protocol Documentation**
   - File: `docs/library/protocol.md`
   - Already has: Section "🔐 Cryptography (`crypto.py`)" with DH/AES-256-GCM spec
   - Your task: **Append implementation details** to that section
   - Add subsection: "### Implementation (Network Class)"
   - Include:
     - Class structure and methods
     - Integration points (Server, Client, DCC)
     - Encryption negotiation flow (diagrams OK)
     - Fallback behavior
   - **Do NOT remove or replace** existing spec
   - Follow markdown style (headers `###`, code blocks, lists)

2. **Server Documentation**
   - File: `docs/library/server.md`
   - Append new section: "## Encryption Support (CSCS)"
   - Describe: How server initiates DH, handles CRYPTOINIT DHREPLY, applies encryption to outbound messages
   - Follow existing format and tone

3. **Client Documentation**
   - File: `docs/library/client.md`
   - Append new section: "## Automatic Encryption (CSCS)"
   - Describe: How client receives CRYPTOINIT DH, responds, auto-encrypts messages
   - Note: Transparent to user (no new commands needed)
   - Follow existing format

4. **Bridge Documentation**
   - File: `docs/library/bridge.md`
   - Append: How bridge relays encrypted CSC traffic unchanged
   - Note: Bridge does NOT re-encrypt (relay as-is)

5. **Updated Library Index**
   - File: `docs/library/INDEX.md`
   - Add new doc if you create one: `docs/library/CSCS_ENCRYPTION.md` (optional, if large)
   - Or just append subsections to existing docs (recommended)

6. **Style & Format Compliance**
   - Use existing markdown style (headers, lists, code blocks, formatting)
   - Mirror tone and structure of existing sections
   - Keep line length reasonable (~80 chars)
   - Include examples where helpful
   - Add diagram if clarifying (ASCII art OK)

---

### Testing Strategy

**Tests must be runnable by test-runner after commit.**

1. **Test File Location**
   - Create: `tests/test_cscs_encryption.py` (or split into multiple: `test_dh.py`, `test_aes_gcm.py`, `test_network.py`)
   - Pattern: Test runner expects `tests/test_*.py` files
   - Check `tests/conftest.py` for fixtures/setup

2. **Test Structure**
   - Use pytest conventions:
     ```python
     import pytest
     from csc_service.shared.network import Network
     from csc_service.shared.dh import DH

     class TestNetwork:
         def test_send_receive_plaintext(self):
             """Plaintext CSC messages work without encryption."""
             pass

         def test_dh_negotiation(self):
             """DH key exchange succeeds."""
             pass

         def test_encrypt_decrypt_roundtrip(self):
             """Messages encrypted and decrypted correctly."""
             pass

         def test_fallback_on_timeout(self):
             """Plaintext fallback if DH times out."""
             pass

     class TestDH:
         def test_keypair_generation(self):
             pass

         def test_shared_secret_computation(self):
             pass
     ```

3. **What to Test**
   - **Unit Tests:**
     - DH key generation (deterministic seed for testing)
     - DH shared secret computation (both sides derive same value)
     - AES-256-GCM encrypt/decrypt round-trip
     - `is_encrypted()` heuristic (plaintext vs. binary)
     - CRYPTOINIT message parsing

   - **Integration Tests:**
     - Server → Client CRYPTOINIT DH flow
     - Client → Server CRYPTOINIT DHREPLY response
     - Encrypted message send/receive end-to-end
     - Fallback: old plaintext client connects to CSCS server
     - Fallback: CSCS client encounters plaintext server

   - **Regression Tests:**
     - Existing plaintext CSC messages still work
     - Server responds to PRIVMSG, JOIN, PART (encrypted and plaintext)
     - Bridge relays messages correctly
     - No interference with existing services

4. **Test Data & Fixtures**
   - Use small DH primes for tests (faster):
     ```python
     @pytest.fixture
     def test_dh_group():
         # Small primes for unit tests (not RFC 3526)
         return {
             'p': 23,  # Small prime for fast testing
             'g': 5,
         }
     ```
   - Use deterministic seeds for reproducibility (if randomness needed)
   - Mock network I/O where appropriate

5. **Running Tests After Commit**
   - Test runner polls every 60s for missing `.log` files in `tests/logs/`
   - After you commit and push, delete: `tests/logs/test_cscs_encryption.log` (if exists)
   - Test runner will detect missing log and re-run `pytest tests/test_cscs_encryption.py`
   - Results written to `tests/logs/test_cscs_encryption.log`
   - If tests fail: test runner generates `PROMPT_fix_test_cscs_encryption.md` for debugging

6. **Test Logging & Output**
   - Use pytest's capture (`capsys`) for output verification
   - Log test progress via `print()` or `logging` module
   - Example:
     ```python
     def test_dh_negotiation(capsys):
         print("Testing DH negotiation...")
         # Test code
         captured = capsys.readouterr()
         assert "success" in captured.out
     ```

7. **Coverage Expectations**
   - Target >80% code coverage (Network, DH, AES-GCM classes)
   - Use `pytest-cov` if available
   - No coverage requirement for test files themselves

---

### Required Testing

Jules should verify:

1. **Unit Tests:**
   - DH key generation and shared secret computation
   - AES-256-GCM encrypt/decrypt round-trip
   - `is_encrypted()` heuristic on plaintext vs. binary

2. **Integration Tests:**
   - Server sends CRYPTOINIT DH, client responds DHREPLY
   - Both derive same shared secret
   - Subsequent messages encrypted end-to-end
   - Fallback works: old plaintext clients still connect

3. **Network Tests:**
   - DCC file transfer encrypted
   - DCC CHAT messages encrypted
   - Bridge relays encrypted traffic unchanged

4. **Stress Tests:**
   - Performance: encryption overhead <5ms per 1KB
   - Concurrent connections: multiple DH negotiations in parallel

---

## Code Maps & References

### Relevant Existing Code

**Shared Library** (`tools/csc-service.txt`):
- Look for: Platform class, Log class, Data class (inheritance chain)
- Pattern: All components inherit from Root → Log → Data → ...
- **Question for Jules:** Should Network inherit from Data for state persistence?

**Server Implementation** (check `server.py` if exists):
- Look for: Message parsing, client registration, message routing
- Integration point: Where to call `network.initiate_encryption()`

**Client Implementation** (check `client.py` or csc-client package):
- Look for: Connection handling, message sending/receiving
- Integration point: Where to handle incoming `CRYPTOINIT DH`

**DCC Implementation** (check DCC support in client.py):
- Look for: DCC SEND/CHAT socket handling
- Integration point: Apply encryption to DCC payload

**Bridge Implementation** (check `bridge.py`):
- Look for: CSC ↔ IRC message translation
- Note: Bridge should NOT re-encrypt relayed traffic

### Documentation References

- **Protocol Spec:** `docs/library/protocol.md` (CRYPTOINIT, AES-256-GCM details)
- **Server Guide:** `docs/library/server.md` (message handler patterns)
- **Client Guide:** `docs/library/client.md` (CSC message format)
- **Bridge Guide:** `docs/library/bridge.md` (relay logic)
- **Project Conventions:** `irc/CLAUDE.md` (coding style, error handling, logging)

### RFC References

- **RFC 3526:** Diffie-Hellman Groups (Group 14 = 2048-bit MODP)
- **RFC 2812:** IRC Protocol (message format)

---

## Success Criteria

✅ All CSC protocol traffic can be encrypted via CSCS
✅ Server and clients auto-negotiate encryption without configuration
✅ Graceful fallback if either party doesn't support encryption
✅ No breaking changes to plaintext CSC clients (backward compatible)
✅ DCC (SEND/CHAT) supports end-to-end encryption
✅ Bridge correctly relays encrypted traffic without re-encryption
✅ Performance acceptable (<5ms overhead per message)
✅ Unit/integration tests verify encryption correctness
✅ Code follows project patterns (logging, error handling, conventions)

---

## Constraints

- ⚠️ **Use only Python stdlib + cryptography library** (if needed; otherwise hashlib/hmac/secrets)
- ⚠️ **Python 3.8+**
- ⚠️ **Encryption state per-connection** (not global)
- ⚠️ **No configuration required** (auto-detect/auto-enable)
- ⚠️ **Backward compatible:** plaintext clients still work

---

## Your Assignment

Implement CSCS encryption layer from this specification, using your own best judgment on:

- Code organization and module structure
- Key derivation strategy (simple vs. HKDF)
- Timeout and fallback behavior
- Connection state storage mechanism
- Logging verbosity
- Testing strategy

The spec above defines **what** to build; **how** you build it is entirely up to you.

---

**Ready to proceed. Use your best engineering judgment.**
