# CampersChromeRestart タスク登録スクリプト
$action = New-ScheduledTaskAction -Execute 'C:\Users\KEISUKE SHIMOMOTO\Desktop\reffort\education\campers\scripts\chrome-restart-for-removal.bat'
$trigger = New-ScheduledTaskTrigger -Daily -At '04:50'
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName 'CampersChromeRestart' -Action $action -Trigger $trigger -Settings $settings -Description 'Chrome restart for Campers member removal (daily 4:50 AM)' -Force
