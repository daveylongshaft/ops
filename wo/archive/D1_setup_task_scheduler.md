# Phase D1: Setup Windows Task Scheduler for Queue Worker

## Task

Configure Windows Task Scheduler to run queue-worker every 2 minutes.

## Requirements

Create a scheduled task that:
- Runs `C:\csc\bin\queue-worker.bat`
- Every 2 minutes
- Runs whether user is logged in or not
- Logs output to `C:\csc\logs\queue-worker.log`

## Implementation

Use PowerShell to create the scheduled task:

```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "C:\csc\bin\queue-worker.bat" -WorkingDirectory "C:\csc"

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 2) -RepetitionDuration ([TimeSpan]::MaxValue)

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName "CSC Queue Worker" -Action $action -Trigger $trigger -Settings $settings -User "SYSTEM" -RunLevel Highest
```

Or use schtasks command:
```batch
schtasks /create /tn "CSC Queue Worker" /tr "C:\csc\bin\queue-worker.bat" /sc minute /mo 2 /ru SYSTEM /rl HIGHEST /f
```

## Verification

Check task was created:
```powershell
Get-ScheduledTask -TaskName "CSC Queue Worker"
```

Test run:
```powershell
Start-ScheduledTask -TaskName "CSC Queue Worker"
```

## Alternative for Cross-Platform

For Linux/Mac, add to crontab:
```bash
*/2 * * * * /opt/csc/bin/queue-worker >> /opt/csc/logs/queue-worker.log 2>&1
```

## Acceptance

- Scheduled task created successfully
- Runs every 2 minutes
- Logs output to queue-worker.log
- Can be started/stopped manually

## Work Log
