---
urgency: P2
agent: haiku
requires: python,google-genai,caching
tags: cache,optimization,cost
blockedBy: gemini-api-workflows-00-skeleton.md
---

# Workorder: Gemini Batch API - Context Caching Manager

## Context
Implement cached content (prompt caching) for Gemini. Cached system context (CLAUDE.md + GEMINI.md + tools index) saves 90% of input tokens. Minimum cache size: 1,024 tokens.

**Related:** Part 8 of 12-part series. Blocked by workorder 00. Optional dependency for workorders 03 (batch), 04 (tool-loop).

## Deliverables

### Create `bin/gemini-batch/gbatch_cache.py`

**CLI Usage:**
```
gbatch_cache.py create [--model gemini-2.5-flash] [--ttl 3600] [--name my-cache]
gbatch_cache.py list
gbatch_cache.py delete <cache_name>
gbatch_cache.py refresh <cache_name> [--ttl 3600]
gbatch_cache.py stats
```

### 1. `CacheManager` Class

**`__init__(self)`:**
- Load `cache_state.json` from `bin/gemini-batch/` if exists
- Initialize empty state if file missing
- Load API key via `common.get_gemini_api_key()`

**State File Format (`cache_state.json`):**
```json
{
  "caches": [
    {
      "name": "csc-context-gemini-2.5-flash",
      "display_name": "CSC System Context",
      "model": "models/gemini-2.5-flash",
      "google_cache_name": "cachedContents/abc123xyz",
      "token_count": 4532,
      "created_at": "2026-03-03T12:00:00Z",
      "expires_at": "2026-03-03T13:00:00Z",
      "ttl_seconds": 3600
    }
  ]
}
```

### 2. `create()` Method
**Signature:** `create(model: str = "gemini-2.5-flash", ttl_seconds: int = 3600, display_name: str = "CSC System Context") -> str`

**Process:**
1. Load system context via `common.load_system_context([CLAUDE.md, GEMINI.md, tools/INDEX.txt, tree.txt])`
2. Verify context > 1,024 tokens (minimum for caching)
3. Generate cache name: `"csc-context-<model_short_name>-<timestamp>"`
   - e.g., `"csc-context-gemini-2.5-flash-20260303-120000"`
4. Create Gemini client, upload cached content:
   ```python
   cached_response = client.caches.create(
       model=model,
       display_name=display_name,
       cached_content=CachedContent(
           parts=[{"text": system_context}],
           usage_metadata={"input_tokens": estimated_count}
       ),
       ttl=Timedelta(seconds=ttl_seconds)
   )
   google_cache_name = cached_response.name  # "cachedContents/..."
   ```
5. Save to `cache_state.json`:
   ```json
   {
     "name": "csc-context-...",
     "display_name": "CSC System Context",
     "model": "models/gemini-2.5-flash",
     "google_cache_name": "cachedContents/abc123",
     "token_count": <count>,
     "created_at": "2026-03-03T12:00:00Z",
     "expires_at": <now + ttl_seconds as ISO string>,
     "ttl_seconds": 3600
   }
   ```
6. Print: `"Created cache 'csc-context-gemini-2.5-flash-...'. Token count: 4532. TTL: 1 hour. Cost savings: ~$0.36 per request."`
7. Return cache name for use in API calls

---

### 3. `get_active(model: str) -> str | None`
**Purpose:** Retrieve the active/valid cache name for a given model.

**Process:**
1. Load `cache_state.json`
2. Filter caches for matching model
3. For each cache:
   - Check if expired (`now > expires_at`)
   - If not expired: return cache name (highest priority: most recent)
   - If expired: log warning, skip
4. If no valid caches: return `None`

**Used by:** workorders 03, 04 to decide whether to include cached content in requests

---

### 4. `list()` Method
**Process:**
1. Load `cache_state.json`
2. For each cache:
   - Print: `[<name>] Model: <model> | Tokens: <count> | Expires: <time> | Status: VALID/EXPIRED`
3. Print summary: `"<N> caches, <M> valid, <P> expired"`

---

### 5. `delete(cache_name: str)` Method
**Process:**
1. Load `cache_state.json`
2. Find cache by name
3. If not found: print error, exit
4. Delete from Google:
   ```python
   client.caches.delete(name=google_cache_name)
   ```
5. Remove from `cache_state.json`
6. Save file
7. Print: `"Deleted cache '<name>'"`

---

### 6. `refresh(cache_name: str, ttl_seconds: int = 3600)` Method
**Purpose:** Extend TTL of an existing cache.

**Process:**
1. Find cache in state
2. If not found: print error, exit
3. Call Google API:
   ```python
   updated = client.caches.update(
       name=google_cache_name,
       ttl=Timedelta(seconds=ttl_seconds)
   )
   ```
4. Update `cache_state.json`: set `expires_at = now + ttl_seconds`
5. Print: `"Refreshed cache '<name>'. New expiration: <time>"`

---

### 7. `stats()` Command
**Purpose:** Show cache statistics and cost savings.

**Process:**
1. Load all caches from state
2. Print:
   - Total valid caches
   - Total tokens cached
   - Potential cost savings if all caches used (e.g., 90% of input tokens saved at $0.15/M)
   - Example: `"5 valid caches, 28,492 total cached tokens. Estimated savings: $0.43 per full batch run."`

---

## Testing Notes
- Unit test: `test_cache_create_and_save()` — mock client, verify state saved
- Unit test: `test_cache_get_active_valid()` — mock non-expired cache, verify returned
- Unit test: `test_cache_get_active_expired()` — mock expired cache, verify None returned
- Unit test: `test_cache_refresh_extends_ttl()` — verify expiration extended
- Unit test: `test_cache_stats_calculation()` — verify cost savings math

## Notes
- TTL is relative to creation time (seconds from now)
- Minimum context size: 1,024 tokens (Google API requirement)
- System context ≈ 4,000-5,000 tokens (CLAUDE.md + GEMINI.md + tools)
- Cost savings: input tokens with cached_read are charged at 10% of normal rate ($0.015/M vs $0.15/M)
- Cache expires after TTL (Google auto-deletes); manager must track expiration locally
- Optional: workorders 03, 04 check `CacheManager.get_active(model)` but work fine without caching
