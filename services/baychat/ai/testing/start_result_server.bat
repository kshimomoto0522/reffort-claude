@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ======================================================================
echo   BayChat AI Reply 再生成APIサーバー
echo   比較HTMLの「補足込みで再生成」ボタンから呼び出されます
echo   停止: Ctrl+C
echo ======================================================================
python result_server.py
pause
