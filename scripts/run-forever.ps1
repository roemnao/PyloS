# Run the bot (or the admin UI) and restart it whenever the process exits.
# Used by install-task.ps1. Manual run:
#   powershell -ExecutionPolicy Bypass -File scripts\run-forever.ps1            (bot)
#   powershell -ExecutionPolicy Bypass -File scripts\run-forever.ps1 -Command admin
# (ASCII only on purpose: Windows PowerShell 5.1 reads BOM-less files as ANSI.)
param(
    [ValidateSet("run", "admin")]
    [string]$Command = "run"
)

$ErrorActionPreference = "Continue"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
$logDir = Join-Path $root "userdata\system\logs"
New-Item -ItemType Directory -Force $logDir | Out-Null
$supervisorLog = Join-Path $logDir "supervisor.log"

Set-Location $root
while ($true) {
    Add-Content -Encoding utf8 $supervisorLog "$(Get-Date -Format s) [$Command] start"
    & $python -m bot $Command
    $code = $LASTEXITCODE
    Add-Content -Encoding utf8 $supervisorLog "$(Get-Date -Format s) [$Command] exited with code $code"
    if ($code -eq 2) {
        # Config error (missing token/key): restarting will not help.
        Add-Content -Encoding utf8 $supervisorLog "$(Get-Date -Format s) [$Command] config error, stopping. Fix userdata\config\settings.env then restart the task."
        exit 2
    }
    if ($code -eq 3) {
        # Another instance already holds the lock in userdata\system\.
        exit 3
    }
    Start-Sleep -Seconds 10
}
