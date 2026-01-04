@echo off
cd /d "%~dp0"

echo.
echo ============================================================
echo   YouTube Chat GUI
echo ============================================================
echo.

REM Zapuskaem GUI napryamuyu cherez venv Python
"%~dp0venv\Scripts\python.exe" "%~dp0chat_gui_simple.py"

if %errorlevel% neq 0 (
    echo.
    echo OSHIBKA pri zapuske GUI!
    pause
)
