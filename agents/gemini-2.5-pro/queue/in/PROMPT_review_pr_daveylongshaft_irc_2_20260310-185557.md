---
role: pr-reviewer
priority: P0
pr: 2
---

# PR Review: #2 — fix: migrate bridge module, fix help_service, fix server main entry point

**Repository**: daveylongshaft/irc
**Author**: daveylongshaft
**Base**: main ← fix/bridge-migration-and-service-bugs

## PR Description

## Summary

- **Bridge migration**: `csc_service.bridge` was missing from the irc repo after the three-repo split. `csc-bridge.service` has been crash-looping with `ModuleNotFoundError` since the split. Copied from `csc_old`.
- **help_service**: Class was named `help` (lowercase) but handler does case-sensitive lookup expecting `Help`. Also fixed `self.server_instance` → `self.server` (attribute doesn't exist).
- **server/main.py**: Entry point `/usr/local/bin/csc-server` does `from csc_service.server.main import main` but `main()` function was missing — only `if __name__ == "__main__": Server().run()` existed.
- **gitignore**: Exclude `buffers/` dir and `bridge/Server_data.json` (runtime state files); untrack `buffers/chan_general.log` from history.

## Test plan
- [ ] `sudo systemctl restart csc-bridge.service && sleep 5 && systemctl is-active csc-bridge.service` → should return `active`
- [ ] `sudo systemctl restart csc-server.service && sleep 5 && systemctl is-active csc-server.service` → should return `active`
- [ ] From IRC: `ai do help` → should return list of services (not error)
- [ ] From IRC: `ai do builtin list_dir .` → should return directory listing

## Changed Files

```
.gitignore
packages/csc-service/csc_service/bridge/__init__.py
packages/csc-service/csc_service/bridge/bridge.py
packages/csc-service/csc_service/bridge/bridge_config.example.json
packages/csc-service/csc_service/bridge/config-local.json
packages/csc-service/csc_service/bridge/config-remote.json
packages/csc-service/csc_service/bridge/config.json
packages/csc-service/csc_service/bridge/control_handler.py
packages/csc-service/csc_service/bridge/data_bridge.py
packages/csc-service/csc_service/bridge/irc.py
packages/csc-service/csc_service/bridge/irc_constants.py
packages/csc-service/csc_service/bridge/irc_normalizer.py
packages/csc-service/csc_service/bridge/irc_utils.py
packages/csc-service/csc_service/bridge/main.py
packages/csc-service/csc_service/bridge/session.py
packages/csc-service/csc_service/bridge/transports/__init__.py
packages/csc-service/csc_service/bridge/transports/base.py
packages/csc-service/csc_service/bridge/transports/tcp_inbound.py
packages/csc-service/csc_service/bridge/transports/tcp_outbound.py
packages/csc-service/csc_service/bridge/transports/udp_inbound.py
packages/csc-service/csc_service/bridge/transports/udp_outbound.py
packages/csc-service/csc_service/buffers/chan_general.log
packages/csc-service/csc_service/server/main.py
packages/csc-service/csc_service/shared/services/help_service.py
```

## Diff (first 60KB)

```diff
(diff unavailable)
```

---

## Your Task

Review PR #2 thoroughly using your role checklist.

For each changed file, read the full file from /opt/csc/<path> — the diff is
context only, bugs hide in what surrounds the change.

Answer:
1. Does it do what the title/description claims?
2. Is it progressive (advances the system) or regressive (undoes work, breaks invariants)?
3. Security implications? (injection, path traversal, hardcoded secrets)
4. Does it break anything outside its stated purpose?
5. Storage still atomic where needed?
6. Any import cascades break?
7. Test coverage adequate?

Post your decision:

  # Approve:
  gh pr review 2 --repo daveylongshaft/irc --approve --body "Your findings"

  # Request changes:
  gh pr review 2 --repo daveylongshaft/irc --request-changes --body "Your specific findings"

Then echo COMPLETE.
