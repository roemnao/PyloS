# Stop and remove the background tasks of the bot and the admin UI.
# (ASCII only on purpose: Windows PowerShell 5.1 reads BOM-less files as ANSI.)
foreach ($taskName in @("ZaloAssistantBot", "ZaloAssistantBotAdmin")) {
    Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Task '$taskName' removed (if it existed)."
}
# Stopping a task only stops powershell; also stop the python processes.
Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
    Where-Object { $_.CommandLine -like "*-m bot run*" -or $_.CommandLine -like "*-m bot admin*" } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
