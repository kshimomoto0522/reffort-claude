@echo off
REM eBay Weekly Report Windows Task wrapper
REM Weekly Monday 10:05 JST via Windows Task Scheduler (WeeklyEbayReport)
REM Replaces Claude scheduled-task `monday-ebay-report-delivery` (2026-05-04 移管)
REM Reason: Claude scheduled-task の承認キャッシュ問題（5/4 月曜の発火がスキップされたため）

setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
set LOG_DIR=%SCRIPT_DIR%logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

set TS=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TS=%TS: =0%
set LOGFILE=%LOG_DIR%\weekly_report_%TS%.log

echo ========================================== >> "%LOGFILE%" 2>&1
echo [%TS%] weekly report start >> "%LOGFILE%" 2>&1
echo ========================================== >> "%LOGFILE%" 2>&1

REM 1. Generate report (Excel + Google Sheets)
python "%SCRIPT_DIR%create_weekly_report_v3.py" >> "%LOGFILE%" 2>&1
set GEN_EXIT=%ERRORLEVEL%
echo [%TS%] generate exit_code=%GEN_EXIT% >> "%LOGFILE%" 2>&1

if not %GEN_EXIT%==0 (
    echo [%TS%] ABORT: generation failed, skipping send >> "%LOGFILE%" 2>&1
    exit /b %GEN_EXIT%
)

REM 2. Send to Chatwork only when generation succeeded
python "%SCRIPT_DIR%send_weekly_report.py" >> "%LOGFILE%" 2>&1
set SEND_EXIT=%ERRORLEVEL%

echo ========================================== >> "%LOGFILE%" 2>&1
echo [%TS%] send exit_code=%SEND_EXIT% >> "%LOGFILE%" 2>&1
echo ========================================== >> "%LOGFILE%" 2>&1

exit /b %SEND_EXIT%
