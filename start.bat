@echo off
cd /d "%~dp0"
echo Starting Year Review Bot...
pip install -r requirements.txt -q >nul 2>&1
python bot.py
pause
