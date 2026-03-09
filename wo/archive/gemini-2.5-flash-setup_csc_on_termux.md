---
requires: [python3, git]
platform: [android, termux]
---
# Set Up CSC on Android (Termux)

## Recommended Agent: gemini-2.5-flash (fast, low resource usage, good for mobile)

## Goal
Install and verify the CSC stack on an Android device running Termux.

## Steps

1. Install prerequisites in Termux:
   ```bash
   pkg install python git
   ```
2. Clone the repo:
   ```bash
   git clone --recursive https://github.com/daveylongshaft/client-server-commander.git
   cd client-server-commander
   ```
3. Install packages:
   ```bash
   pip install -e packages/csc-shared
   pip install -e packages/csc-server
   pip install -e packages/csc-client
   ```
4. Verify platform detection:
   ```bash
   python -c "from csc_shared.platform import Platform; p = Platform(); print(p.platform_data['os'])"
   ```
   Should show `is_android: True` and `distribution: android-termux`
5. Start the server: `csc-server`
6. Start the client in another Termux session: `csc-client`
7. Run the Android platform test: `python -m pytest tests/test_platform_android.py -v`
8. Commit any Termux-specific fixes needed, push

## Key concerns
- Limited RAM and CPU — resource_level should be "minimal" or "low"
- No Docker available
- No systemd — use Termux:Boot for autostart
- pkg instead of apt for package management
- File paths are under /data/data/com.termux
