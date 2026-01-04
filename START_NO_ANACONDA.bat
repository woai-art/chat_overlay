@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo   YOUTUBE CHAT DLY VMIX (BEZ ANACONDA!)
echo ============================================================
echo.

REM Ubiraem VSE puti s Anaconda iz PATH
set "PATH=%PATH:C:\ProgramData\anaconda3;=%"
set "PATH=%PATH:C:\ProgramData\anaconda3\Scripts;=%"
set "PATH=%PATH:C:\ProgramData\anaconda3\Library\bin;=%"
set "PATH=%PATH:C:\ProgramData\Anaconda3;=%"
set "PATH=%PATH:C:\ProgramData\Anaconda3\Scripts;=%"
set "PATH=%PATH:%USERPROFILE%\anaconda3;=%"
set "PATH=%PATH:%USERPROFILE%\anaconda3\Scripts;=%"
set "PATH=%PATH:%USERPROFILE%\Anaconda3;=%"
set "PATH=%PATH:%USERPROFILE%\Anaconda3\Scripts;=%"

REM Ubiraem peremenniye Anaconda
set CONDA_DEFAULT_ENV=
set CONDA_PREFIX=
set CONDA_PROMPT_MODIFIER=
set CONDA_SHLVL=
set CONDA_PYTHON_EXE=
set CONDA_EXE=

echo [OK] Anaconda otklyuchena dlya etoy sessii.
echo.

REM Proveryaem OAuth
if not exist youtube_oauth_token.json (
    echo VNIMANIE: OAuth avtorizaciya ne proydena!
    echo.
    echo Dlya raboti parsera nuzhna OAuth avtorizaciya.
    echo Zapustite START.bat -^> opciya 2 dlya avtorizacii.
    echo.
    pause
)

REM Absolutnie puti
set PROJECT_DIR=%~dp0
set VENV_PYTHON=%PROJECT_DIR%venv\Scripts\python.exe

echo Zapuskayutsya vse komponenti:
echo   - HTTP server (port 8080)
echo   - GUI dlya nastroek
echo.

REM Zapusk HTTP servera cherez wrapper (garantirovanno venv!)
echo Zapusk HTTP servera...
start "YouTube Chat - HTTP Server" "%PROJECT_DIR%_run_server.bat"

echo Ozhidanie zapuska servera...
timeout /t 3 /nobreak >nul

REM Zapusk GUI cherez wrapper (garantirovanno venv!)
echo Zapusk GUI nastroek...
start "YouTube Chat - GUI" "%PROJECT_DIR%_run_gui.bat"

echo Ozhidanie zapuska GUI...
timeout /t 2 /nobreak >nul

echo Otkritie chata v brauzere...
start "" "http://localhost:8080/vmix_simple.html"

echo.
echo ============================================================
echo   Sistema zapushchena BEZ Anaconda!
echo ============================================================
echo.
echo Chto delat dalshe:
echo   1. V GUI vvedite URL YouTube translyacii
echo   2. Nazhmite "Zapustit parser" v GUI
echo   3. Ispolzuyte http://localhost:8080/vmix_simple.html v vMix
echo.
echo PROVERTE: Zapustite CHECK_PARSERS.bat
echo Dolzhni bit TOLKO processi iz venv (ne Anaconda)!
echo.
pause
