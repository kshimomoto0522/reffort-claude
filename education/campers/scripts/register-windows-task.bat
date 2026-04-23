@echo off
REM =====================================================================
REM Windowsタスクスケジューラ登録スクリプト
REM
REM 機能:
REM   Chrome再起動タスクを毎日4:50 AMに実行するよう登録する。
REM
REM タスク名: CampersChromeRestart
REM 実行時刻: 毎日 04:50
REM 実行内容: chrome-restart-for-removal.bat を実行
REM
REM 注意:
REM   このスクリプトを実行すると既存の同名タスクは上書きされる (/F)
REM =====================================================================

setlocal
set TASK_NAME=CampersChromeRestart
set BAT_PATH=%~dp0chrome-restart-for-removal.bat

echo Windowsタスクスケジューラに登録します...
echo タスク名: %TASK_NAME%
echo 実行対象: %BAT_PATH%
echo 実行時刻: 毎日 04:50
echo.

schtasks /create /TN "%TASK_NAME%" /TR "\"%BAT_PATH%\"" /SC DAILY /ST 04:50 /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =====================================================================
    echo 登録に成功しました。
    echo.
    echo 確認コマンド:
    echo   schtasks /query /TN "%TASK_NAME%"
    echo.
    echo 削除コマンド:
    echo   schtasks /delete /TN "%TASK_NAME%" /F
    echo =====================================================================
) else (
    echo.
    echo =====================================================================
    echo 登録に失敗しました。管理者権限で実行してください。
    echo =====================================================================
)

endlocal
pause
