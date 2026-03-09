# Platform Cross-System Implementation - Batch Workorders

## Overview

This directory contains sequential workorders for implementing cross-platform service installation and management. The work is divided into clear, bite-sized tasks suitable for Gemini Flash models running via the Gemini API.

**Goal:** Make CSC services automatically configure and run on Windows, Linux, WSL, macOS, and Android without manual per-system setup.

---

## Workorder Sequence

All workorders depend on platform_00 through their chain. Work them in order for minimal rework.

### Phase 1: Platform Detection Extensions (platform_00 through platform_03)

| # | Name | Duration | Dependency | Summary |
|---|------|----------|-----------|---------|
| **00** | Extend platform.py RuntimeStrategy | 45 min | None | Detect available runtimes (native, WSL, Docker) |
| **01** | Add PathTranslator Class | 50 min | 00 | Auto-translate paths between Windows/WSL/Docker/Linux formats |
| **02** | Add CommandBuilder Class | 50 min | 00, 01 | Generate platform-specific shell commands with correct syntax |
| **03** | Extend platform.json Schema | 30 min | 00, 01, 02 | Update schema to include runtime, paths, and service config |

**Subtotal:** ~3.25 hours

### Phase 2: Service Detection (platform_04 and platform_05)

| # | Name | Duration | Dependency | Summary |
|---|------|----------|-----------|---------|
| **04** | Windows Service Detection | 40 min | 00-03 | Detect CSC-* Windows services via PowerShell |
| **05** | Linux/systemd Detection | 40 min | 00-03 | Detect csc-* systemd services on Linux/WSL |

**Subtotal:** ~1.33 hours

### Phase 3: Service Management (platform_06 through platform_09)

| # | Name | Duration | Dependency | Summary |
|---|------|----------|-----------|---------|
| **06** | ServiceManager Core Class | 45 min | 04, 05 | Unified service manager with platform-specific routing |
| **07** | Windows Service Installation (NSSM) | 50 min | 04, 06 | Install/manage Windows services with NSSM |
| **08** | Linux/systemd Installation | 50 min | 05, 06 | Install/manage systemd services on Linux/WSL |
| **09** | Add csc-ctl Service Commands | 45 min | 06-08 | CLI commands: service install/uninstall/start/stop/status |

**Subtotal:** ~3.75 hours

### Phase 4: Testing & Verification (platform_10)

| # | Name | Duration | Dependency | Summary |
|---|------|----------|-----------|---------|
| **10** | Test Service Installation | 60 min | 00-09 | Verify implementation on Windows, Linux, WSL |

**Subtotal:** 1 hour

---

## Grand Total

**~9.33 hours of implementation** split across 11 workorders.

Estimated API usage:
- **Gemini 2.5 Flash** (cheapest): All 11 workorders
- If quota exhausted: Switch to **Gemini 3.0 Flash Preview**
- If all quota exhausted: Batch remaining with **prompt caching + Haiku**

---

## Running the Batch

### Option A: Sequential on Single Agent

Assign all to one Gemini agent (e.g., gemini-2.5-flash-lite) and let it work through them sequentially:

```bash
csc-ctl assign platform_00 gemini-2.5-flash-lite
csc-ctl assign platform_01 gemini-2.5-flash-lite
# ... etc
```

### Option B: Parallel Batches

Assign in groups (3-4 workorders per agent) to speed up:

```bash
# Agent 1
csc-ctl assign platform_00 gemini-2.5-flash-lite
csc-ctl assign platform_01 gemini-2.5-flash-lite
csc-ctl assign platform_02 gemini-2.5-flash-lite

# Agent 2 (when ready)
csc-ctl assign platform_03 gemini-3.0-flash-preview
csc-ctl assign platform_04 gemini-3.0-flash-preview
csc-ctl assign platform_05 gemini-3.0-flash-preview

# ... etc
```

### Option C: Batch API + Prompt Caching

When API quota exhausted:

1. Create batch file with remaining workorders
2. Add system prompt with `cache_control` (Anthropic only)
3. Run batch with Haiku + prompt caching
4. Higher throughput, lower cost

---

## Workorder Structure

Each workorder includes:

- **Objective**: What the task accomplishes
- **Dependencies**: Prerequisite workorders
- **Time Estimate**: How long it typically takes
- **Task**: Clear, specific work
- **Implementation**: Code snippets, class definitions, patterns to follow
- **Integration**: How to integrate with existing code
- **Testing**: Test script to verify the implementation
- **Verification Checklist**: Line-by-line confirmation of success
- **Commit Template**: Suggested git commit message

---

## Key Files Modified

Across all workorders:

- `packages/csc-shared/csc_shared/platform.py` — Extended with runtime, path, command classes
- `packages/csc-shared/csc_shared/platform_service_windows.py` — New file, Windows service detection + NSSM installation
- `packages/csc-shared/csc_shared/platform_service_linux.py` — New file, Linux/systemd service detection + installation
- `packages/csc-shared/csc_shared/platform_service_manager.py` — New file, unified service manager
- `packages/csc-service/csc_service/infra/ctl.py` — Extended with service commands
- `platform.json` — Schema extended with runtime_strategy, paths, services, bootstrap_status

---

## Success Criteria

After all 11 workorders complete:

1. **Platform detection** automatically identifies runtime (native, WSL, Docker)
2. **Path translation** handles Windows ↔ WSL ↔ Docker ↔ Linux automatically
3. **Service installation** works on Windows (NSSM), Linux/WSL (systemd)
4. **CLI commands** (`csc-ctl service install all`) just work on any system
5. **No manual per-system configuration** needed — automatic detection + setup
6. **Cross-platform commands** (csc-ctl start server, stop queue, etc.) work everywhere

---

## Notes for Agents

### For Gemini Flash Models

- Each workorder is self-contained
- Code examples are copy-paste ready
- Test instructions are clear and specific
- Don't need to understand the full architecture — just follow the instructions
- Commit messages are templated; fill in test results

### For PR Review (Opus/Gemini-3-Pro)

These changes:
- ✓ Extend platform detection (already exists)
- ✓ Add service management (new but contained)
- ✓ Update CLI with new commands (additive)
- ✓ No breaking changes to existing functionality
- ✓ All changes backward compatible

Single review sufficient (not infrastructure-critical).

---

## Testing Each Workorder

**Golden Rule:** Every workorder includes a test script. Run it before committing.

- platform_00-03: Import and verify classes load
- platform_04-05: List services (may return empty if none installed)
- platform_06: Verify manager routes to correct provider
- platform_07-08: Install test service, verify status, uninstall
- platform_09: Test CLI commands
- platform_10: Full integration test on your system

---

## What's Next After This Batch

Once complete:

1. **Bootstrap Agent** workorder: Haiku agent configures new systems on first run
2. **Docker Compose** support: Extend to docker-compose services
3. **macOS launchd** support: When someone tests on Mac
4. **Android service** support: When someone tests on Android

For now, Windows + Linux + WSL cover ~95% of development needs.

---

## Questions?

Each workorder is detailed enough to work independently. If anything is unclear:
- Read the workorder file completely
- Check the integration section for context
- Look at the test script for expected behavior
- If still stuck, mark blockers and document in commit message

Good luck! 🚀

