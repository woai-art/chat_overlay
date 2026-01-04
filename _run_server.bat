@echo off
REM Wrapper dlya zapuska servera TOLKO cherez venv
cd /d "%~dp0"
"%~dp0venv\Scripts\python.exe" "%~dp0simple_server.py" 8080

