@echo off
REM BayChat Slack Check Windows Task wrapper
REM Every 30 min via Windows Task Scheduler (BayChatSlackCheck)
REM Replaces Claude scheduled-task `baychat-slack-hourly-check` (2026-04-29 移管)

setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
set LOG_DIR=%SCRIPT_DIR%logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

set TS=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TS=%TS: =0%
set LOGFILE=%LOG_DIR%\slack_check_%TS%.log

echo ========================================== >> "%LOGFILE%" 2>&1
echo [%TS%] baychat-slack-check start >> "%LOGFILE%" 2>&1
echo ========================================== >> "%LOGFILE%" 2>&1

python "%SCRIPT_DIR%baychat_slack_check.py" >> "%LOGFILE%" 2>&1
set EXIT_CODE=%ERRORLEVEL%

echo ========================================== >> "%LOGFILE%" 2>&1
echo [%TS%] exit_code=%EXIT_CODE% >> "%LOGFILE%" 2>&1
echo ========================================== >> "%LOGFILE%" 2>&1

exit /b %EXIT_CODE%
