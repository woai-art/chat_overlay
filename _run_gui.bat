@echo off
REM Wrapper dlya zapuska GUI TOLKO cherez venv
cd /d "%~dp0"
"%~dp0venv\Scripts\python.exe" "%~dp0chat_gui_simple.py"




