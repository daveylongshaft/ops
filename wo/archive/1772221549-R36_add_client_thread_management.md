# R36: Add Client Thread Management to Main Loop

## Depends: R14, R19, R20, R21

## Task
Add optional threading support to run AI clients (claude, gemini, chatgpt) as
background threads managed by the main loop, controlled by csc-service.json.

## Steps

1. Open `packages/csc-service/csc_service/main.py`

2. Add threading imports at the top:
```python
import threading
```

3. After the subsystem status print (before the `while True` loop), add client thread startup:
```python
    # Start enabled client threads
    client_threads = {}
    clients_config = config.get("clients", {})
    for client_name, client_cfg in clients_config.items():
        if client_cfg.get("enabled") and client_cfg.get("auto_start"):
            try:
                if client_name == "claude":
                    from csc_service.clients.claude.main import main as client_main
                elif client_name == "gemini":
                    from csc_service.clients.gemini.main import main as client_main
                elif client_name == "chatgpt":
                    from csc_service.clients.chatgpt.main import main as client_main
                else:
                    continue
                t = threading.Thread(target=client_main, name=f"client-{client_name}", daemon=True)
                t.start()
                client_threads[client_name] = t
                print(f"[{ts()}] [csc-service] Started client: {client_name}")
            except Exception as e:
                print(f"[{ts()}] [csc-service] Failed to start {client_name}: {e}")
```

4. In the main loop, add a health check for client threads:
```python
    # Check client thread health
    for name, t in list(client_threads.items()):
        if not t.is_alive():
            print(f"[{ts()}] [csc-service] Client {name} thread died")
            del client_threads[name]
```

## Verification
- `grep "threading" packages/csc-service/csc_service/main.py` finds the import
- `grep "client_threads" packages/csc-service/csc_service/main.py` finds the dict


DEAD END - csc-service package already consolidated and operational
