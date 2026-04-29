@echo off
REM Campers member removal Windows Task wrapper
REM Daily 5:00 AM via Task Scheduler
REM Logs Python output to dated log file

setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
set LOG_DIR=%SCRIPT_DIR%logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

set TS=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TS=%TS: =0%
set LOGFILE=%LOG_DIR%\removal_%TS%.log

echo ========================================== >> "%LOGFILE%" 2>&1
echo [%TS%] Campers member removal start >> "%LOGFILE%" 2>&1
echo ========================================== >> "%LOGFILE%" 2>&1

python "%SCRIPT_DIR%campers_member_removal.py" >> "%LOGFILE%" 2>&1
set EXIT_CODE=%ERRORLEVEL%

echo ========================================== >> "%LOGFILE%" 2>&1
echo [%TS%] exit_code=%EXIT_CODE% >> "%LOGFILE%" 2>&1
echo ========================================== >> "%LOGFILE%" 2>&1

if %EXIT_CODE% neq 0 (
    python "%SCRIPT_DIR%_fallback_notify.py" %EXIT_CODE% "%LOGFILE%" >> "%LOGFILE%" 2>&1
)

exit /b %EXIT_CODE%
