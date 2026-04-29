#Requires -Version 5.1
# Windowsタスクスケジューラに CampersMemberRemoval を登録（毎朝5:00）

$ErrorActionPreference = 'Stop'

$TaskName = 'CampersMemberRemoval'
$BatPath = 'C:\Users\KEISUKE SHIMOMOTO\Desktop\reffort\education\campers\scripts\run_campers_removal.bat'

if (-not (Test-Path $BatPath)) {
    Write-Error ('Batch script not found: ' + $BatPath)
}

# 既存があれば削除
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host 'Removing existing task...'
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$action = New-ScheduledTaskAction -Execute $BatPath
$trigger = New-ScheduledTaskTrigger -Daily -At '05:00'
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit ([TimeSpan]::FromMinutes(15)) -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description 'Campers member removal (Playwright). Daily 5:00 AM.'

Write-Host "Task registered: $TaskName"
Get-ScheduledTask -TaskName $TaskName | Select-Object TaskName, State, @{n='NextRunTime';e={(Get-ScheduledTaskInfo $_).NextRunTime}} | Format-List
