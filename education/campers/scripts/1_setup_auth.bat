@echo off
REM Chatwork Playwright認証セットアップ（初回のみ・cookie切れ時のみ）
cd /d "%~dp0"
python setup_chatwork_auth.py
pause
