@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo   TEST ZAPUSKA GUI
echo ============================================================
echo.

echo Proverka venv Python...
if not exist "venv\Scripts\python.exe" (
    echo OSHIBKA: venv\Scripts\python.exe ne nayden!
    pause
    exit /b 1
)

echo venv Python nayden: venv\Scripts\python.exe
echo.

echo Zapusk GUI...
venv\Scripts\python.exe chat_gui_simple.py

echo.
echo GUI zakryto.
pause

