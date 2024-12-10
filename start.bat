@echo off
cd /d "C:\Users\dev04\agenda"
call .venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8010
pause
