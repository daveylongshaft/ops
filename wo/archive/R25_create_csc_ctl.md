> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# R25: Create csc-ctl Management CLI

## Depends: R24

## Task
Create `packages/csc-service/csc_service/ctl.py` — a CLI tool to enable/disable
components in `csc-service.json`.

## Steps
Create `packages/csc-service/csc_service/ctl.py`:

```python
"""csc-ctl: manage csc-service configuration.

Usage:
    csc-ctl status                    # show what's enabled
    csc-ctl enable <component>        # enable a component
    csc-ctl disable <component>       # disable a component
    csc-ctl set poll_interval 30      # set a config value

Components: test-runner, queue-worker, pm, server, claude, gemini, chatgpt
"""
import json
import sys
from pathlib import Path

def find_config():
    """Find csc-service.json walking up from cwd."""
    p = Path.cwd()
    while p != p.parent:
        cfg = p / "csc-service.json"
        if cfg.exists():
            return cfg
        p = p.parent
    # Default location
    return Path.cwd() / "csc-service.json"

def load_config(path):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}

def save_config(path, config):
    path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

COMPONENT_MAP = {
    "test-runner": "enable_test_runner",
    "queue-worker": "enable_queue_worker",
    "pm": "enable_pm",
    "server": "enable_server",
    "claude": "clients.claude.enabled",
    "gemini": "clients.gemini.enabled",
    "chatgpt": "clients.chatgpt.enabled",
}

def set_nested(config, dotpath, value):
    """Set a nested key like 'clients.claude.enabled'."""
    parts = dotpath.split(".")
    d = config
    for part in parts[:-1]:
        d = d.setdefault(part, {})
    d[parts[-1]] = value

def get_nested(config, dotpath, default=None):
    parts = dotpath.split(".")
    d = config
    for part in parts:
        if isinstance(d, dict) and part in d:
            d = d[part]
        else:
            return default
    return d

def cmd_status(config):
    print("csc-service status:")
    for name, key in COMPONENT_MAP.items():
        val = get_nested(config, key, False)
        state = "ON" if val else "OFF"
        print(f"  {name:15s} {state}")
    pi = config.get("poll_interval", 60)
    print(f"\n  poll_interval:  {pi}s")

def cmd_enable(config, component):
    if component not in COMPONENT_MAP:
        print(f"Unknown component: {component}")
        print(f"Valid: {', '.join(COMPONENT_MAP.keys())}")
        return False
    set_nested(config, COMPONENT_MAP[component], True)
    print(f"Enabled {component}")
    return True

def cmd_disable(config, component):
    if component not in COMPONENT_MAP:
        print(f"Unknown component: {component}")
        print(f"Valid: {', '.join(COMPONENT_MAP.keys())}")
        return False
    set_nested(config, COMPONENT_MAP[component], False)
    print(f"Disabled {component}")
    return True

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return

    cfg_path = find_config()
    config = load_config(cfg_path)

    cmd = args[0]
    if cmd == "status":
        cmd_status(config)
    elif cmd == "enable" and len(args) > 1:
        if cmd_enable(config, args[1]):
            save_config(cfg_path, config)
    elif cmd == "disable" and len(args) > 1:
        if cmd_disable(config, args[1]):
            save_config(cfg_path, config)
    elif cmd == "set" and len(args) > 2:
        key, val = args[1], args[2]
        try:
            val = int(val)
        except ValueError:
            try:
                val = float(val)
            except ValueError:
                if val.lower() in ("true", "false"):
                    val = val.lower() == "true"
        config[key] = val
        save_config(cfg_path, config)
        print(f"Set {key} = {val}")
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
```

## Verification
- `pip install -e packages/csc-service`
- `csc-ctl` prints usage
- `csc-ctl status` shows component states
- `csc-ctl enable claude` updates csc-service.json
- `csc-ctl disable claude` updates csc-service.json
