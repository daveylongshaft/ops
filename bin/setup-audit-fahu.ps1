# setup-audit-fahu.ps1
# Run on fahu (Windows) to prepare the audit working environment.
# Usage: powershell -ExecutionPolicy Bypass -File setup-audit-fahu.ps1

$AuditRoot = "C:\fahu\audit"
$NewRoot   = "$AuditRoot\csc_new"
$OldRoot   = "$AuditRoot\csc_old"

Write-Host "[audit] Setting up $AuditRoot"
New-Item -ItemType Directory -Force -Path $AuditRoot | Out-Null

# --- csc_new: umbrella repo with irc + ops submodules ---
if (-not (Test-Path "$NewRoot\.git")) {
    Write-Host "[audit] Cloning csc.git -> $NewRoot"
    git clone https://github.com/daveylongshaft/csc.git $NewRoot
    git -C $NewRoot submodule update --init --recursive
} else {
    Write-Host "[audit] csc_new exists, pulling"
    git -C $NewRoot pull --rebase --autostash
    git -C $NewRoot submodule update --remote --merge
}

# --- csc_old: original monorepo ---
if (-not (Test-Path "$OldRoot\.git")) {
    Write-Host "[audit] Cloning client-server-commander.git -> $OldRoot"
    # Authenticate via gh CLI or set GITHUB_TOKEN in env before running
    git clone https://github.com/daveylongshaft/client-server-commander.git $OldRoot
} else {
    Write-Host "[audit] csc_old exists, pulling"
    git -C $OldRoot pull --rebase --autostash
}

Write-Host ""
Write-Host "[audit] Ready:"
Write-Host "  csc_new : $NewRoot"
Write-Host "    irc   : $NewRoot\irc"
Write-Host "    ops   : $NewRoot\ops"
Write-Host "  csc_old : $OldRoot"
Write-Host ""
Write-Host "Next: pick up the audit WO from $NewRoot\ops\wo\ready\"
