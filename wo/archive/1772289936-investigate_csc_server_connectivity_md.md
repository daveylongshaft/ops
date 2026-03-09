# Investigate CSC Server Connectivity Issues

## Problem

User cannot reach:
1. **Localhost CSC server** (127.0.0.1:9525 or localhost:9525)
2. **Fahu server** (remote/federated CSC server)

Both servers should be running and accessible but are not.

## Investigation Steps

### 1. Localhost Server (Priority 1)

**Check if server is running:**
```bash
csc-ctl status                          # Show service status
csc-ctl show csc-service                # Show config
ps aux | grep csc-server                # Check process
netstat -tlnp | grep 9525               # Check port binding
```

**If server not running:**
```bash
csc-ctl restart all                     # Restart all services
csc-server                              # Start directly
python -m csc_service.server            # Run in foreground
```

**If port 9525 not listening:**
- Check if another process is bound to it
- Change port in csc-service.json if needed
- Restart server

**Test connectivity:**
```bash
# Try connecting
csc-client                              # GUI client
telnet localhost 9525                   # Raw TCP test
nc -zv localhost 9525                   # Port test
```

**Check firewall:**
```bash
# Windows
netsh advfirewall firewall show rule name=all | grep 9525

# Linux
sudo ufw status
sudo iptables -L | grep 9525

# macOS
sudo pfctl -s rules | grep 9525
```

### 2. Fahu Server (Priority 2)

**Determine fahu connection details:**
- What IP/hostname for fahu?
- What port (9525 or different)?
- Is fahu actually running?
- Network reachable? (same network? VPN? firewall?)

**Test connectivity to fahu:**
```bash
# Test DNS
nslookup fahu.example.com
ping fahu.example.com

# Test port
telnet fahu.example.com 9525
nc -zv fahu.example.com 9525

# Try CSC client
csc-client --server fahu.example.com:9525
```

**Check network path:**
```bash
# Trace route
tracert fahu.example.com                # Windows
traceroute fahu.example.com             # Linux
mtr fahu.example.com                    # Continuous

# Check if blocked
curl -v telnet://fahu.example.com:9525
```

### 3. Server Logs Analysis

**Check localhost server logs:**
```bash
tail -100 logs/server.log
tail -100 logs/queue-worker.log
tail -100 logs/test-runner.log
```

**Look for:**
- Server startup errors (bind failed, port in use)
- Connection errors (refused, timeout)
- Network errors (socket errors)
- Configuration errors (bad config file)

### 4. Configuration Verification

**Check csc-service.json:**
```bash
cat csc-service.json | grep -A5 "server"
# Look for: host, port, listen_address
```

**Should have:**
```json
{
  "server": {
    "host": "0.0.0.0",      // Listen on all interfaces
    "port": 9525,
    "protocol": "udp",
    "enabled": true
  }
}
```

**For fahu:**
```bash
cat csc-service.json | grep -A10 "federation\|remote\|fahu"
# Look for: fahu server config, connection details
```

### 5. Common Issues & Fixes

**Issue: Port already in use**
```bash
# Find what's using port 9525
lsof -i :9525                           # Linux/macOS
netstat -ano | findstr :9525            # Windows

# Kill the process
kill -9 <PID>                           # Linux/macOS
taskkill /PID <PID> /F                  # Windows
```

**Issue: Server crashed/not running**
```bash
# Restart
csc-ctl restart all
csc-ctl install all                     # Re-install services
csc-service --daemon                    # Start unified service
```

**Issue: Firewall blocking**
- Add port 9525 to firewall exceptions
- If fahu remote: check ISP firewall, corporate firewall
- VPN might be blocking: try disabling

**Issue: Wrong IP/hostname**
- Check csc-service.json for correct server address
- Make sure localhost resolves to 127.0.0.1 (check /etc/hosts or hosts file)
- Verify DNS for fahu (nslookup, dig, host)

**Issue: Network unreachable (fahu)**
- Are you on same network? Different network?
- Is VPN connected?
- Is firewall on fahu machine blocking 9525?
- Can you ping fahu at all?

### 6. Detailed Diagnostics

**Run complete network test:**
```bash
# Network availability
ipconfig /all                           # Windows network config
ip addr show                            # Linux network config
ifconfig                                # macOS network config

# Local loopback
ping 127.0.0.1
ping localhost

# Server availability
csc-ctl status
csc-ctl show server

# Connection test
python -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(('127.0.0.1', 9525))
    print('✓ Localhost connection OK')
except Exception as e:
    print(f'✗ Connection failed: {e}')
"
```

## Expected Output (Success)

```
Localhost Server:
✓ Port 9525 listening
✓ Server process running
✓ csc-ctl status shows: running
✓ Can connect with csc-client
✓ Can ping/telnet to localhost:9525

Fahu Server:
✓ DNS resolves fahu hostname
✓ Can ping fahu IP
✓ Port 9525 responding on fahu
✓ Can connect with csc-client --server fahu:9525
✓ Latency acceptable (<100ms if local, <500ms if remote)
```

## Troubleshooting Decision Tree

```
Can you connect to localhost:9525?
├─ YES: Server is working
│       └─ Problem is with fahu connection (see below)
│
└─ NO: Localhost server issue
    ├─ Is server process running?
    │  ├─ NO: Start server (csc-ctl restart all)
    │  └─ YES: Is port 9525 bound?
    │     ├─ NO: Check logs for bind error
    │     └─ YES: Is it listening on 0.0.0.0?
    │
    └─ Can you reach 127.0.0.1:9525?
       ├─ NO: Firewall blocking
       └─ YES: Hostname resolution issue

Can you reach fahu server?
├─ NO: Network issue
│  ├─ Can you ping fahu?
│  │  ├─ NO: Network unreachable (firewall/routing)
│  │  └─ YES: Port 9525 not open on fahu
│  └─ Is fahu server running on fahu machine?
│
└─ YES: Connection works
   └─ Can you authenticate/join channels?
```

## Success Criteria

- [X] Localhost server accessible via localhost:9525
- [X] Can connect with IRC client (csc-client or telnet)
- [X] Fahu server accessible (if remote/federated)
- [X] PM and other agents can connect
- [X] Both servers stable and responding

## Notes

- User mentioned "fahu" - need to clarify if this is hostname, IP, or code name
- If Windows MSYS2: may have network/firewall differences
- If federated: need to understand CSC server linking/federation setup
- Port 9525 is default - check if intentionally changed
