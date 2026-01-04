@echo off
cd /d "%~dp0"

echo ============================================================
echo   DIAGNOSTIKA GUI
echo ============================================================
echo.

REM Proverka venv
if not exist "venv\Scripts\python.exe" (
    echo [OSHIBKA] venv\Scripts\python.exe ne nayden!
    echo.
    echo Reshenie: sozdayte venv komandoy:
    echo   python -m venv venv
    echo.
    pause
    exit /b 1
)

echo [OK] venv Python nayden: venv\Scripts\python.exe
echo.

REM Proverka fayla GUI
if not exist "chat_gui_simple.py" (
    echo [OSHIBKA] chat_gui_simple.py ne nayden!
    pause
    exit /b 1
)

echo [OK] chat_gui_simple.py nayden
echo.

REM Proverka importov
echo [TEST] Proverka importov...
venv\Scripts\python.exe -c "import tkinter; print('[OK] tkinter importirovan')" 2>&1
if errorlevel 1 (
    echo [OSHIBKA] tkinter ne ustanovlen!
    echo.
    echo Reshenie: ustanovite tkinter:
    echo   venv\Scripts\pip install tk
    echo.
    pause
    exit /b 1
)

echo.
echo [TEST] Zapusk GUI s vyvodom oshibok...
echo ============================================================
echo.

venv\Scripts\python.exe chat_gui_simple.py 2>&1

echo.
echo ============================================================
echo GUI zakryto.
echo.
pause

