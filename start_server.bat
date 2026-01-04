@echo off
cd /d "%~dp0"

echo.
echo ============================================================
echo   HTTP Server
echo ============================================================
echo.

REM Zapuskaem server napryamuyu cherez venv Python
"%~dp0venv\Scripts\python.exe" "%~dp0simple_server.py" 8080

if %errorlevel% neq 0 (
    echo.
    echo OSHIBKA pri zapuske servera!
    pause
)
