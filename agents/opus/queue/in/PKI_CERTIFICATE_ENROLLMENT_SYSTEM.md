# PKI Certificate Enrollment System

## Purpose

Automated TLS certificate lifecycle for CSC S2S links. New servers request
certs via Apache-proxied enrollment endpoint on haven.ef6e. PKI service writes
all cert events to a log file. Botserv watches that log and announces to #general.

---

## Architecture

### Enrollment flow (new server, no cert)

1. Admin issues token on IRC: `PKI TOKEN [shortname]` → returns one-time token
2. New server runs: `csc-ctl enroll https://haven.ef6e/csc/pki/ <token>`
3. csc-ctl generates private key + CSR, CN = server shortname (from `server_name` file)
4. POST `{ shortname, csr_pem, token }` to enrollment endpoint
5. PKI service validates token, calls EasyRSA `sign-req`, returns cert chain PEM
6. csc-ctl stores `/etc/csc/<shortname>.key` (600) and `/etc/csc/<shortname>.chain.pem`
7. PKI service writes to `/opt/csc/logs/pki.log` → botserv picks it up → #general

### Auto-renewal / revocation detection (every server startup + every 12h)

`Platform.check_s2s_cert()` runs before S2S listener starts:
- No cert file → log warning, S2S listener does not start
- Cert expiring within 30 days → POST `/csc/pki/renew` (mTLS, existing cert authenticates)
- Cert serial in CRL → stop S2S, WALLOPS all admins, require new enrollment token

### CRL refresh

All servers: every 12h, GET `/csc/pki/crl.pem` → save to `/etc/csc/crl.pem`

---

## PKI Log Format

All events written to `/opt/csc/logs/pki.log` as they occur:

```
2026-03-11T02:30:00 [PKI] cert issued:  haven.ef6e  valid 2026-03-11 → 2027-03-11
2026-03-11T02:31:00 [PKI] cert renewed: crest.a2b3  valid 2026-03-11 → 2027-03-11
2026-03-11T02:32:00 [PKI] cert revoked: old.xxxx    CRL updated and propagated
2026-03-11T02:33:00 [PKI] enrollment pending: unknown token consumed, queued for signing
```

### Botserv wiring (run once after PKI service is live)

```
AI do botserv addmatch #general \[PKI\]
AI do botserv logread #general /opt/csc/logs/pki.log
```

Periodic trigger: server-side timer (add `pki_logread_interval` to csc-service.json,
default 60s) calls `botserv.logread("#general", "/opt/csc/logs/pki.log")` internally.

---

## New Files

### `packages/csc-service/csc_service/server/services/pki_service.py`
IRC command handler — oper-only (requires `a` or `A` flag for write ops):

| Command | Flags | Action |
|---------|-------|--------|
| `PKI TOKEN [shortname]` | a/A | Generate one-time enrollment token, print it |
| `PKI LIST` | o | Show all issued certs: shortname, expiry, status |
| `PKI REVOKE <shortname>` | a/A | Revoke cert, regenerate CRL, write to pki.log |
| `PKI STATUS` | o | CA health, CRL age, token count, issued certs |
| `PKI PENDING` | o | Show tokens issued but not yet used |

### `packages/csc-service/csc_service/pki/enrollment_server.py`
WSGI app on `127.0.0.1:9530`:

| Route | Method | Auth | Action |
|-------|--------|------|--------|
| `/enroll` | POST | token in body | Validate token, sign CSR, return cert chain, write pki.log |
| `/renew` | POST | mTLS (existing cert) | Reissue cert, return new chain, write pki.log |
| `/ca.crt` | GET | none | Serve CA certificate |
| `/crl.pem` | GET | none | Serve current CRL |

### `packages/csc-service/csc_service/pki/main.py`
Entry point — runs as in-proc thread in csc-service (`enable_pki: true` in csc-service.json).

### `bin/csc-ctl` additions
New subcommand `csc-ctl enroll <ca_url> <token>`:
- Calls `Platform.get_server_shortname()` for CN
- Generates key + CSR with `cryptography` or `openssl` subprocess
- POSTs to enrollment endpoint
- Writes `/etc/csc/<shortname>.key` (chmod 600) and `/etc/csc/<shortname>.chain.pem`
- Prints confirmation

New subcommand `csc-ctl cert status`:
- Reads `/etc/csc/<shortname>.chain.pem`
- Shows: CN, serial, not-before, not-after, days remaining
- Checks serial against local CRL → shows revoked/valid

---

## Modified Files

### `csc_service/shared/platform.py`
Add `check_s2s_cert()` classmethod:
- Reads `s2s_cert` path from `csc-service.json`
- Returns `(ok: bool, reason: str)`
- Called from `server.py __init__` before S2S listener starts

### `csc_service/server/server.py`
In `__init__`: call `Platform.check_s2s_cert()`, log result, skip S2S if not ok.

### `csc_service/cli/commands/service_cmd.py` + `status_cmd.py`
Add `pki` to `INPROC_SERVICES` map.

### Apache config
File: `/opt/csc/etc/apache-pki.conf` (symlinked into `/etc/apache2/conf-enabled/`):
```apache
<Location /csc/pki/>
    ProxyPass http://127.0.0.1:9530/
    ProxyPassReverse http://127.0.0.1:9530/
</Location>
```
HTTPS only — redirect HTTP → HTTPS for this path.

---

## EasyRSA Integration

Existing CA:
```
/etc/openvpn/easy-rsa/easyrsa
/etc/openvpn/easy-rsa/pki/ca.crt
/etc/openvpn/easy-rsa/pki/crl.pem
```

Signing workflow inside enrollment_server.py:
```bash
cd /etc/openvpn/easy-rsa
./easyrsa --batch import-req /tmp/<shortname>.csr <shortname>
./easyrsa --batch sign-req server <shortname>
cat pki/issued/<shortname>.crt pki/ca.crt > /etc/csc/<shortname>.chain.pem
./easyrsa gen-crl                          # refresh CRL after any sign/revoke
cp pki/crl.pem /etc/csc/crl.pem
```

Token storage: `/opt/csc/tmp/csc/run/pki_tokens.json`
```json
{
  "<token_hex>": {
    "shortname": "crest.a2b3",
    "created_at": 1741234567,
    "used": false
  }
}
```
Tokens expire after 24h. One token per shortname at a time.

---

## Cert Storage Layout

```
/etc/csc/
  haven.ef6e.key          private key    (600, csc_user only)
  haven.ef6e.chain.pem    cert + CA      (644)
  crl.pem                 current CRL    (644, refreshed every 12h)
  ca.crt                  CA cert        (644)
```

`csc-service.json` additions:
```json
"s2s_cert": "/etc/csc/haven.ef6e.chain.pem",
"s2s_key":  "/etc/csc/haven.ef6e.key",
"s2s_ca":   "/etc/csc/ca.crt",
"s2s_crl":  "/etc/csc/crl.pem",
"pki_ca_url": "https://haven.ef6e/csc/pki/",
"enable_pki": false
```

Set `enable_pki: true` on the CA server (haven.ef6e) only.

---

## Verification

```
# On haven.ef6e (CA server):
PKI TOKEN crest.a2b3          # generates enrollment token
PKI STATUS                    # show CA health

# On new server:
csc-ctl enroll https://haven.ef6e/csc/pki/ <token>
csc-ctl cert status

# #general should show:
# [PKI] cert issued: crest.a2b3  valid 2026-03-11 → 2027-03-11

# Revocation test:
PKI REVOKE crest.a2b3
# #general should show:
# [PKI] cert revoked: crest.a2b3  CRL updated and propagated
```


--- Agent Log ---
Already up to date.
Current branch main is up to date.
Invoking: gemini -y -m gemini-2.5-pro -p " " (cwd: /opt, repo: /opt/clones/gemini-2.5-pro/PKI_CERTIFICATE_ENROLLMENT_SYSTEM-1773216376/repo)
[WARN] Skipping unreadable directory: /opt/csc/.config/configstore (EACCES: permission denied, scandir '/opt/csc/.config/configstore')
YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
[WARN] Skipping unreadable directory: /opt/csc/.config/configstore (EACCES: permission denied, scandir '/opt/csc/.config/configstore')
YOLO mode is enabled. All tool calls will be automatically approved.
Hook registry initialized with 0 hook entries
Error when talking to Gemini API Full report available at: /tmp/gemini-client-error-Turn.run-sendMessageStream-2026-03-11T08-06-51-651Z.json TerminalQuotaError: You have exhausted your capacity on this model. Your quota will reset after 14h59m50s.
    at classifyGoogleError (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/googleQuotaErrors.js:214:28)
    at retryWithBackoff (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/retry.js:131:37)
    at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
    at async GeminiChat.makeApiCallAndProcessStream (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:431:32)
    at async GeminiChat.streamWithRetries (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:263:40)
    at async Turn.run (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/turn.js:66:30)
    at async GeminiClient.processTurn (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/client.js:459:26)
    at async GeminiClient.sendMessageStream (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/client.js:559:20)
    at async file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/dist/src/nonInteractiveCli.js:193:34
    at async main (file:///home/davey/.nvm/versions/node/v22.20.0/lib/node_modules/@google/gemini-cli/dist/src/gemini.js:492:9) {
  cause: {
    code: 429,
    message: 'You have exhausted your capacity on this model. Your quota will reset after 14h59m50s.',
    details: [ [Object], [Object] ]
  },
  retryDelayMs: 53990407.987101
}
An unexpected critical error occurred:[object Object]

[INFO] Agent execution completed
[INFO] Log: /opt/csc/ops/logs/gemini-2.5-pro_1773216377.log


--- Verify/Complete or Finish ---
Please verify this workorder is complete or finish the work and add COMPLETE as the last line.

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)
