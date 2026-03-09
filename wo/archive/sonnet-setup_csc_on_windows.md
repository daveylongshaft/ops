---
requires: [python3, git]
platform: [windows]
---
# Set Up CSC on Windows

## Recommended Agent: sonnet (moderate complexity, environment setup)

## Goal
Install and verify the full CSC stack on a Windows machine.

## Steps

1. Clone the repo: `git clone --recursive https://github.com/daveylongshaft/client-server-commander.git`
2. Install packages:
   ```bash
   pip install -e packages/csc-shared
   pip install -e packages/csc-server
   pip install -e packages/csc-client
   ```
3. Verify platform detection:
   ```bash
   python -c "from csc_shared.platform import Platform; p = Platform(); print(p.platform_data['os'])"
   ```
4. Start the server: `csc-server`
5. In another terminal, start the client: `csc-client`
6. Verify connection works
7. Run the Windows platform test: `python -m pytest tests/test_platform_windows.py -v`
8. Commit any Windows-specific fixes needed, push

## Key concerns
- UDP socket handling may differ on Windows
- File paths use backslash — check atomic storage works
- ctypes RAM detection via GlobalMemoryStatus
- No /proc/meminfo — fallback must work
