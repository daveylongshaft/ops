# Task: Add FIFO-Based Daemon Mode to csc-client

## Goal

Make `csc-client` runnable as a systemd daemon by using a named pipe (FIFO) for input and a regular file for output. This lets AI agents and scripts send commands to a live IRC/CSC session by writing to the FIFO, and read server responses from the output file.

## Background

The client already supports `--infile` and `--outfile` flags, but ONLY when run directly via `python3.10 client.py` (the `__main__` block at line 1484 of `client.py`). The problem is that `--infile` reads a regular file to EOF and then exits. For daemon mode we need the input to stay open indefinitely, which is exactly what a FIFO does — reads block until a writer opens the pipe.

**CRITICAL — Dual Entry Point Bug:** There are two entry points and they don't agree:
- `packages/csc-client/main.py` (what systemd uses) — calls `Client().run()` with **zero arguments**. All CLI flags are silently ignored.
- `packages/csc-client/client.py` `__main__` block (line 1484) — has argparse and passes flags through to `Client()`.

**You MUST fix `main.py`** so that CLI flags actually reach the `Client` constructor. Either move argparse into `main.py`'s `main()` function, or have `main.py` call `client.py`'s `__main__` logic. The simplest fix is to add argparse to `main.py` and pass the args through:

```python
def main():
    import argparse
    from csc_client.client import Client

    parser = argparse.ArgumentParser(description="CSC IRC Client")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--infile", help="File to read commands from ('-' for stdin)")
    parser.add_argument("--outfile", help="File to write output to")
    parser.add_argument("--detach", action="store_true", help="Run without interactive input")
    parser.add_argument("--fifo", action="store_true",
        help="Daemon mode: read commands from /run/csc/client.in FIFO")
    args = parser.parse_args()

    # FIFO mode setup
    input_file = args.infile
    output_file = args.outfile
    interactive = not args.detach

    if args.fifo:
        from pathlib import Path
        fifo_dir = Path("/run/csc")
        fifo_dir.mkdir(parents=True, exist_ok=True)
        fifo_path = fifo_dir / "client.in"
        if not fifo_path.exists():
            os.mkfifo(str(fifo_path))
        input_file = str(fifo_path)
        if not output_file:
            output_file = str(fifo_dir / "client.out")
        interactive = False

    client = Client(config_path=args.config, output_file=output_file, input_file=input_file)
    client.run(interactive=interactive)
```

Then remove or simplify the duplicate argparse in `client.py`'s `__main__` block to just call `main()` or defer to `main.py`.

## What Needs to Change

### 1. Create the FIFO and output file paths

Standard locations:
- **Input FIFO**: `/run/csc/client.in` (named pipe)
- **Output file**: `/run/csc/client.out` (regular file, append mode)
- **Directory**: `/run/csc/` (owned by `csc_user:csc_group`, mode 770)

### 2. Modify `_input_loop()` in `packages/csc-client/client.py`

The current `input_file` code path (line 718-733) reads the file to EOF and returns. For a FIFO, the read loop must **reopen the pipe** after EOF (which happens when the last writer closes their end) instead of exiting. The fix:

```python
def _input_loop(self):
    if self.input_file:
        while self._running:
            try:
                with open(self.input_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not self._running:
                            break
                        line = line.strip()
                        if line:
                            self.process_command(line)
                            time.sleep(0.1)
                # EOF means all writers closed the pipe — reopen and wait
            except Exception as e:
                self._write_to_output(f"[Client ERROR] FIFO read error: {e}")
                time.sleep(1)
        return
    # ... rest of interactive input_loop unchanged ...
```

Key difference: the `while self._running` outer loop reopens the file on EOF instead of returning.

### 3. Add `--fifo` flag (in `main.py` — see Background section above)

The `--fifo` flag and all argparse logic belongs in `main.py` since that is the entry point systemd calls. See the code example in the Background section. Do NOT add it only to `client.py`'s `__main__` block — that path is not used by systemd.

### 4. Update the systemd service file

Update `/etc/systemd/system/csc-client.service`:

```ini
[Unit]
Description=CSC Human Client (FIFO Daemon)
After=network.target csc-server.service

[Service]
Type=simple
User=csc_user
Group=csc_group
WorkingDirectory=/opt/csc/client
ExecStartPre=/bin/mkdir -p /run/csc
ExecStartPre=/bin/bash -c 'test -p /run/csc/client.in || mkfifo /run/csc/client.in'
ExecStartPre=/bin/chown csc_user:csc_group /run/csc /run/csc/client.in
ExecStart=/usr/bin/python3.10 main.py --fifo
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=csc-client
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

### 5. Add csc-client to restart_csc.sh

Once this works, add `csc-client` back to the `SERVICES` array in `/opt/csc/bin/restart_csc.sh` and enable the service.

## How AI Agents Use It

Once the service is running, any process on the system can send commands:

```bash
# Send a message to current channel
echo "hello from the script" > /run/csc/client.in

# Send IRC commands
echo "/join #test" > /run/csc/client.in
echo "/msg NickName hey there" > /run/csc/client.in

# Send multiple commands
cat <<'EOF' > /run/csc/client.in
/join #dev
hello everyone
/names
EOF

# Read recent output
tail -50 /run/csc/client.out
```

Each `echo` or write opens the FIFO, writes, and closes it. The client sees the line, processes it, and blocks again waiting for the next writer. This is the standard FIFO pattern — no special client needed on the writing end.

## Testing

1. Manual test without systemd first:
   ```bash
   mkfifo /tmp/csc-test.in
   python3.10 main.py --infile /tmp/csc-test.in --outfile /tmp/csc-test.out &
   echo "/names" > /tmp/csc-test.in
   cat /tmp/csc-test.out
   ```
2. Verify the client does NOT exit after the first echo
3. Verify multiple successive writes all get processed
4. Verify the client reconnects the FIFO after writer disconnects

## Files to Modify

- `packages/csc-client/main.py` — **add argparse here** with all flags (`--config`, `--infile`, `--outfile`, `--detach`, `--fifo`) and pass them through to `Client()` constructor and `run()`. This is the entry point systemd uses.
- `packages/csc-client/client.py` — FIFO reopen loop in `_input_loop()`. Also clean up the `__main__` block (line 1484) to avoid duplicate argparse — either remove it or have it call `main.py`'s `main()`.
- `/etc/systemd/system/csc-client.service` — update for FIFO daemon mode
- `/opt/csc/bin/restart_csc.sh` — add csc-client back once enabled

## Important Notes

- The FIFO blocks on open until a writer connects — this is desired behavior, not a hang
- Multiple writers can write to the same FIFO safely (kernel serializes writes under PIPE_BUF, 4096 bytes on Linux — single-line commands are fine)
- Output file will grow indefinitely — consider adding logrotate or a max-size trim (the client's `_write_to_output` already timestamps lines)
- Do NOT use a FIFO for output — readers would steal lines from each other. Use a regular file that multiple consumers can `tail -f`
