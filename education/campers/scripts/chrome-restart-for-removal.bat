@echo off
REM =====================================================================
REM Campersメンバー削除タスク用 Chrome再起動スクリプト
REM
REM 目的:
REM   毎朝5:00のメンバー削除タスク前に、Chrome拡張機能（Claude in Chrome）の
REM   Service Workerがハングした状態をリセットする。
REM
REM 動作:
REM   1. 実行中のChromeプロセスを全て終了
REM   2. 3秒待機
REM   3. Chromeを --restore-last-session で再起動（タブ復元）
REM   4. 60秒待機（拡張機能の初期化完了を待つ）
REM
REM 前提:
REM   Chromeの設定「前回開いていたページから続行」がONであること。
REM   （chrome://settings/onStartup で確認可能）
REM
REM 実行タイミング:
REM   Windowsタスクスケジューラで毎日4:50 AMに実行
REM
REM ログ出力:
REM   実行結果を chrome-restart.log に追記
REM =====================================================================

setlocal
set LOG_FILE=%~dp0chrome-restart.log
set CHROME_EXE="C:\Program Files\Google\Chrome\Application\chrome.exe"

echo. >> "%LOG_FILE%"
echo ===== %DATE% %TIME% ===== >> "%LOG_FILE%"

REM Step 1: 既存のChromeプロセスを全て終了
echo [1] Chromeプロセス終了中... >> "%LOG_FILE%"
taskkill /IM chrome.exe /F >> "%LOG_FILE%" 2>&1

REM Step 2: プロセス終了を待つ
echo [2] 3秒待機中... >> "%LOG_FILE%"
timeout /t 3 /nobreak > nul

REM Step 3: Chromeを復元起動
echo [3] Chromeを復元起動中... >> "%LOG_FILE%"
start "" %CHROME_EXE% --restore-last-session

REM Step 4: 拡張機能初期化待ち
echo [4] 60秒待機中（拡張機能初期化）... >> "%LOG_FILE%"
timeout /t 60 /nobreak > nul

echo [5] 完了 >> "%LOG_FILE%"
endlocal
