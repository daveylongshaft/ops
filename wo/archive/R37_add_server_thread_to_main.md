> **DEAD END** — csc-service consolidation already complete as of 2026-03-08. Do not execute.

# R37: Add Server Thread to Main Loop

## Depends: R36

## Task
Add optional IRC server as a background thread, controlled by `enable_server` in config.

## Steps

1. Open `packages/csc-service/csc_service/main.py`

2. After the client thread startup block, add server startup:
```python
    # Start server thread if enabled
    server_thread = None
    if config.get("enable_server", False):
        try:
            from csc_service.server.main import main as server_main
            server_thread = threading.Thread(target=server_main, name="server", daemon=True)
            server_thread.start()
            print(f"[{ts()}] [csc-service] Started IRC server")
        except Exception as e:
            print(f"[{ts()}] [csc-service] Failed to start server: {e}")
```

3. In the health check section, add:
```python
    if server_thread and not server_thread.is_alive():
        print(f"[{ts()}] [csc-service] Server thread died")
        server_thread = None
```

## Verification
- `grep "server_thread" packages/csc-service/csc_service/main.py` finds references
- With `enable_server: false` in config, server does NOT start
