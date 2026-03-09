# AI Message Filtering & Wakeword System

## Problem

AI agents currently receive ALL channel text, wasting API tokens on irrelevant chatter. They should only receive messages that are actually directed at them or relevant to them.

## Requirements

### 1. Server-Side Message Filter for AI Clients

In `server_message_handler.py`, before forwarding a PRIVMSG to an AI client on a channel, check whether the message matches ANY of:

- **Nick match**: Message contains the AI's nickname (case-insensitive)
  - e.g. "Claude what do you think?" -> forward to Claude
- **AI command token**: Message starts with the AI command prefix (currently `AI `)
  - e.g. "AI do agent status" -> forward to all AI clients
- **Wakeword match**: Message contains any word/phrase from the client's enabled wakeword list
  - e.g. if "help" is a wakeword and someone says "I need help" -> forward

If NONE match, do NOT forward the PRIVMSG to that AI client. Human clients always get everything.

How to know if a client is AI: check if the nick has wakeword filtering enabled (see section 3).

### 2. Wakeword Service (`wakeword_service.py`)

New service in `packages/csc_shared/services/` with commands:

```
wakeword add <word_or_phrase>    - Add a wakeword (case-insensitive)
wakeword del <word_or_phrase>    - Remove a wakeword
wakeword list                    - Show all wakewords
```

Accessed via: `AI do wakeword add help` / `AI do wakeword list` etc.

Storage: `wakewords.json` in server working directory, atomic write pattern like all other storage:
```json
{
  "words": ["help", "bug", "error", "review", "deploy"]
}
```

The wakeword list is global (shared by all AI clients that enable it).

### 3. Client Opt-In via WAKEWORD Command

AI agents enable filtering at connect time with a raw IRC command:

```
WAKEWORD ENABLE
WAKEWORD DISABLE
```

Sent via `/quote WAKEWORD ENABLE` from client or raw socket.

- **Default: DISABLED** (all messages forwarded as normal, backward compatible)
- Server tracks which connected clients have wakeword filtering enabled in the client session dict
- Add handler `handle_wakeword()` in `server_message_handler.py`
- Register WAKEWORD in `_dispatch_irc_command`

### 4. AI Command Response Line Prefixing

When an AI processes an `AI do ...` command and sends back a multi-line response, **every line** of the response MUST be prefixed with the AI command token (`AI `).

This ensures responses are clearly identifiable as AI command output vs normal chat.

Example:
```
<user> AI do agent status
<Claude> AI Agent: sonnet | RUNNING
<Claude> AI   PID: 12345 | Elapsed: 2m 30s
<Claude> AI   Prompt: PROMPT_fix_test.md
```

This prefixing should happen server-side in the AI command response routing, NOT in the AI client itself. The server wraps each line before sending to channel.

### 5. Integration Points

**server_message_handler.py changes:**
- `handle_privmsg()`: Before forwarding to each channel member, check if recipient has wakeword filtering enabled. If yes, check nick/token/wakeword match. Skip if no match.
- `handle_wakeword()`: New handler for WAKEWORD ENABLE/DISABLE command.
- AI command response routing: Wrap each response line with AI prefix.

**server.py changes:**
- Client session dict needs a `wakeword_enabled: bool` field (default False)
- Load/access wakewords.json (can be on-demand @property like opers)

**New file:**
- `packages/csc_shared/services/wakeword_service.py`

**Storage:**
- `wakewords.json` - atomic write, same pattern as all other storage

### 6. Testing

Write `tests/test_wakeword.py`:
- Test wakeword add/del/list
- Test message filtering: nick match forwards, wakeword match forwards, no match blocks
- Test WAKEWORD ENABLE/DISABLE command
- Test AI command response line prefixing
- Test default-disabled backward compatibility
- Test case-insensitive matching

## Implementation Notes

- Check `tools/csc-server.txt` code map before reading source
- Wakeword matching should be efficient (compile word list into a set, check with `any(w in message_lower for w in wakewords)`)
- Phrase matching (multi-word wakewords) needs substring check, not word boundary
- Do NOT break existing behavior for clients that never send WAKEWORD command
