# Document & Test: cryptserv service

## Task
1. Read `services/cryptserv_service.py` — document every public method
2. Add a `cryptserv` section to `docs/services.md` under "Security & Identity Services" (create if missing)
3. Write `tests/test_cryptserv_service.py`

## Documentation
- Document every command with syntax and description
- Explain what crypto operations are available
- Note any external dependencies (gpg, openssl subprocess calls, python libs)

## Tests
- Mock the server instance
- Test each crypto operation with known inputs/outputs
- Test error handling: bad input, missing dependencies
- Use `unittest.TestCase`
- File: `tests/test_cryptserv_service.py`

read services/cryptserv_service.py
read docs/services.md
update docs/services.md
write tests/test_cryptserv_service.py
check structure of docs/services.md
update docs/services.md
write tests/test_cryptserv_service.py
commit
move
push

---

## DEAD END — 2026-03-10

`cryptserv_service.py` does not yet exist. Service is not built out.
Documentation and tests deferred until implementation is complete.

---

## Planning Notes — CryptServ Architecture

### Concept
Server-mediated RSA key distribution for encrypted IRC traffic. The server
acts as a CA and holds all keys, allowing it to decrypt traffic while still
providing encryption layers above the DH/AES transport layer.

### Key Exchange Types

**Channel encryption**
- Server generates a channel key pair per channel
- All channel members receive the channel key to participate
- Channel text encrypted with the channel key — possession of key = access

**Client-to-client (DM/group)**
- Server generates a per-pair (or per-N-party) key for each conversation
- Keys distributed to each party member via PRIVMSG/NOTICE/DCC CHAT
- Two-party: unique keypair per user+user combination
- Three-party+: server generates session key, distributes to all parties

### Transport Layering
```
DH/AES (transport)          ← always on, wire encryption
  └── channel key (AES)     ← per-channel, membership gating
        └── user-pair key   ← per-conversation, for DMs/group chat
```

### Server Role
- Provides both private and public keys for each exchange
- Can decrypt all traffic (by design — operator visibility)
- Manages key lifecycle: generation, distribution, rotation, revocation

### Open Questions (resolve before implementation)
- Key storage: in-memory only vs persisted (atomic storage pattern)
- Key rotation policy: per-session, timed, on-member-change
- DCC CHAT support: needs translator bridge to handle key negotiation
- Forward secrecy trade-off: server holding private keys means no FS
- Command surface: `cryptserv request <target>`, `cryptserv rotate <target>`, `cryptserv revoke <target>`

### Status
Not pressing. Revisit with thorough planning session before commencing implementation.
