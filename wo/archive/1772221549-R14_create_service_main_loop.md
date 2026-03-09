# R14: Create csc-service Main Loop

## Depends: R10, R11, R12, R13

## Task
Create the main entry point that runs all subsystems in a unified loop.

## Steps
1. Create `packages/csc-service/csc_service/main.py` with this content:

```python
"""csc-service: unified service manager for CSC.

Usage:
    csc-service --daemon              # run all subsystems
    csc-service --daemon --local      # run on cwd (no clone)
    csc-service --daemon --dir /path  # run in specific directory
"""
import sys
import time
import json
from pathlib import Path

def main():
    args = sys.argv[1:]

    # Determine working directory
    csc_root = Path(__file__).resolve().parent.parent.parent  # packages/csc-service/csc_service -> csc/
    work_dir = csc_root  # default: local mode
    poll_interval = 60

    # Parse args
    if "--dir" in args:
        idx = args.index("--dir")
        work_dir = Path(args[idx + 1])

    # Load config
    config_file = csc_root / "csc-service.json"
    config = {}
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text(encoding='utf-8'))
        except Exception:
            pass

    poll_interval = config.get("poll_interval", 60)
    enable_test_runner = config.get("enable_test_runner", True)
    enable_queue_worker = config.get("enable_queue_worker", True)
    enable_pm = config.get("enable_pm", True)

    # Setup subsystems
    from csc_service.infra import git_sync
    git_sync.setup(work_dir)

    if "--daemon" in args:
        ts = lambda: time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts()}] [csc-service] Starting (poll every {poll_interval}s)")
        print(f"[{ts()}] [csc-service] Work dir: {work_dir}")
        print(f"[{ts()}] [csc-service] Subsystems: "
              f"test-runner={'ON' if enable_test_runner else 'OFF'} "
              f"queue-worker={'ON' if enable_queue_worker else 'OFF'} "
              f"pm={'ON' if enable_pm else 'OFF'}")

        try:
            while True:
                # 1. Sync
                git_sync.pull()

                # 2. Run subsystems
                if enable_test_runner:
                    try:
                        from csc_service.infra import test_runner
                        # test_runner.run_cycle() - wired after import refactor
                        pass
                    except Exception as e:
                        print(f"[{ts()}] [test-runner] ERROR: {e}")

                if enable_queue_worker:
                    try:
                        from csc_service.infra import queue_worker
                        # queue_worker.run_cycle() - wired after import refactor
                        pass
                    except Exception as e:
                        print(f"[{ts()}] [queue-worker] ERROR: {e}")

                if enable_pm:
                    try:
                        from csc_service.infra import pm
                        pm.setup(work_dir)
                        assigned = pm.run_cycle()
                        for wo, agent in assigned:
                            print(f"[{ts()}] [pm] Assigned {wo} -> {agent}")
                    except Exception as e:
                        print(f"[{ts()}] [pm] ERROR: {e}")

                # 3. Push changes
                git_sync.push_if_changed()

                time.sleep(poll_interval)

        except KeyboardInterrupt:
            print(f"\n[{ts()}] [csc-service] Stopped")
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
```

## Verification
- `pip install -e packages/csc-service`
- `csc-service` prints usage
- `csc-service --daemon --local` starts and prints subsystem status
- Ctrl+C stops cleanly


DEAD END - csc-service package already consolidated and operational
