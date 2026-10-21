@echo off
cd /d "%~dp0"
python -m pip install -r requirements.txt
python -m uvicorn server.main:app --host 127.0.0.1 --port 8080
pause
