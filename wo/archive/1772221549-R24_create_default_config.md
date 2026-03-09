# R24: Create Default csc-service.json Config

## Depends: R01

## Task
Create the default config file at the project root.

## Steps
Create `csc-service.json` in the project root (`/opt/csc/csc-service.json` or `C:\csc\csc-service.json`):

```json
{
  "poll_interval": 60,
  "enable_test_runner": true,
  "enable_queue_worker": true,
  "enable_pm": true,
  "enable_server": false,
  "enable_clients": {},
  "clients": {
    "claude": {
      "enabled": false,
      "auto_start": false
    },
    "gemini": {
      "enabled": false,
      "auto_start": false
    },
    "chatgpt": {
      "enabled": false,
      "auto_start": false
    }
  },
  "git_sync": {
    "enabled": true,
    "push_after_cycle": true
  }
}
```

Also add `csc-service.json` to `.gitignore` (it contains local config):
```bash
echo "csc-service.json" >> .gitignore
```

And create a `csc-service.json.example` that IS committed (same content as above).

## Verification
- `cat csc-service.json` shows valid JSON
- `cat csc-service.json.example` shows the template
- `grep csc-service.json .gitignore` finds it


DEAD END - csc-service package already consolidated and operational
