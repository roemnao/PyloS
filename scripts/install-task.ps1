# Register Task Scheduler tasks so the bot and the admin UI start when you log on
# to Windows and keep running in the background.
#   Install:   powershell -ExecutionPolicy Bypass -File scripts\install-task.ps1
#   Bot only:  powershell -ExecutionPolicy Bypass -File scripts\install-task.ps1 -NoAdmin
#   Uninstall: powershell -ExecutionPolicy Bypass -File scripts\uninstall-task.ps1
# (ASCII only on purpose: Windows PowerShell 5.1 reads BOM-less files as ANSI.)
param([switch]$NoAdmin)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$script = Join-Path $PSScriptRoot "run-forever.ps1"

if (-not (Test-Path (Join-Path $root ".venv\Scripts\python.exe"))) {
    throw "Missing .venv. See README.md, section 'Cai dat'."
}
if (-not (Test-Path (Join-Path $root ".env"))) {
    throw "Missing .env. Copy .env.example to .env and fill in ZALO_BOT_TOKEN and GEMINI_API_KEY."
}

function Register-BotTask([string]$TaskName, [string]$Command, [string]$Description) {
    $action = New-ScheduledTaskAction -Execute "powershell.exe" `
        -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$script`" -Command $Command" `
        -WorkingDirectory $root
    $trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
        -StartWhenAvailable -ExecutionTimeLimit ([TimeSpan]::Zero) `
        -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) `
        -MultipleInstances IgnoreNew
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings `
        -Description $Description -Force | Out-Null
    Start-ScheduledTask -TaskName $TaskName
    Write-Host "Task '$TaskName' registered and started."
}

Register-BotTask "ZaloAssistantBot" "run" "Zalo assistant bot (auto restart)"
if (-not $NoAdmin) {
    Register-BotTask "ZaloAssistantBotAdmin" "admin" "Zalo assistant bot - admin UI on http://127.0.0.1:8081 (auto restart)"
}
Write-Host "Logs: $root\logs\bot.log, $root\logs\admin.log"
