@echo off
cd /d "%~dp0"
py -m venv venv
call venv\Scripts\activate.bat
py -m pip install -r requirements.txt
pause
