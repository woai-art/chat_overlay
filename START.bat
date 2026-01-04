@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

REM Deaktiviruem Anaconda esli ona aktivna
if defined CONDA_DEFAULT_ENV (
    echo Deaktivaciya Anaconda...
    call conda deactivate 2>nul
)

REM Udalяem Anaconda iz PATH dlya etoy sessii
set "PATH=%PATH:C:\ProgramData\anaconda3;=%"
set "PATH=%PATH:C:\ProgramData\anaconda3\Scripts;=%"
set "PATH=%PATH:C:\ProgramData\Anaconda3;=%"
set "PATH=%PATH:C:\ProgramData\Anaconda3\Scripts;=%"
set "PATH=%PATH:%USERPROFILE%\anaconda3;=%"
set "PATH=%PATH:%USERPROFILE%\anaconda3\Scripts;=%"
set "PATH=%PATH:%USERPROFILE%\Anaconda3;=%"
set "PATH=%PATH:%USERPROFILE%\Anaconda3\Scripts;=%"

REM Dobavlyaem venv v PATH PERVIM
set "PATH=%~dp0venv\Scripts;%PATH%"

:MENU
cls
echo.
echo ==========================================
echo     YOUTUBE CHAT DLY VMIX
echo ==========================================
echo.
echo Viberite deystvie:
echo.
echo   1. Polniy zapusk (Server + Parser + GUI)
echo   2. OAuth avtorizaciya YouTube (NOVOE!)
echo   3. Tolko veb-server
echo   4. Tolko GUI nastroek
echo   5. Otkrit chat v brauzere
echo   6. Proverka zapushchennih processov
echo   7. Sbrosit nastroyki chata (esli GUI ne zapuskaetsya)
echo   8. Ostanovit vse processi
echo   9. Vihod
echo.
echo ==========================================
echo.
set /p choice="Vvedite nomer (1-9): "

if "!choice!"=="1" goto FULL_START
if "!choice!"=="2" goto OAUTH_AUTH
if "!choice!"=="3" goto SERVER_ONLY
if "!choice!"=="4" goto GUI_ONLY
if "!choice!"=="5" goto OPEN_BROWSER
if "!choice!"=="6" goto CHECK_PARSERS
if "!choice!"=="7" goto RESET_SETTINGS
if "!choice!"=="8" goto KILL_ALL
if "!choice!"=="9" goto END
goto MENU

:OAUTH_AUTH
echo.
echo ==========================================
echo      OAUTH AVTORIZACIYA YOUTUBE
echo ==========================================
echo.

if not exist client_secret.json (
    echo VNIMANIE: Fayl client_secret.json ne nayden!
    echo.
    echo Dlya OAuth nuzhno sozdat credentials v Google Cloud Console.
    echo Instrukciya v fayle: GOOGLE_OAUTH_SETUP.md
    echo.
    set /p open_console="Otkrit Google Console? (y/n): "
    if /i "!open_console!"=="y" (
        echo.
        echo Otkritie Google Console...
        start "" "https://console.cloud.google.com/"
        start "" "QUICK_OAUTH_GUIDE.txt"
        echo.
        echo Posle sozdaniya client_secret.json zapustite etu opciyu snova
        echo.
        goto END
    )
    echo.
    echo Bez client_secret.json OAuth ne budet rabotat!
    echo.
    goto END
)

echo Fayl client_secret.json nayd

en!
echo.
echo Otkroetsya brauzer dlya avtorizacii.
echo Voydite v YouTube/Google i razreshite dostup.
echo.
pause

REM Absolutniy put k proektu
set PROJECT_DIR=%~dp0
set VENV_PYTHON=%PROJECT_DIR%venv\Scripts\python.exe

echo.
echo Zapusk OAuth avtorizacii...
echo.

"%VENV_PYTHON%" youtube_auth.py

echo.
if exist youtube_oauth_token.json (
    echo Avtorizaciya uspeshna!
    echo Teper mozhete zapuskat parser ^(opciya 1^)
) else (
    echo Avtorizaciya ne zavershena
)
echo.
goto END

:FULL_START
echo.
echo ==========================================
echo      POLNIY ZAPUSK SISTEMI
echo ==========================================
echo.

if not exist youtube_oauth_token.json (
    echo VNIMANIE: OAuth avtorizaciya ne proydena!
    echo.
    echo Dlya raboti parsera nuzhna OAuth avtorizaciya.
    echo.
    set /p oauth_choice="Proyti avtorizaciyu seychas? (y/n): "
    if /i "!oauth_choice!"=="y" (
        goto OAUTH_AUTH
    )
    echo.
    echo Parser mozhet ne rabotat bez OAuth!
    echo Rekomenduetsya proyti avtorizaciyu ^(opciya 2^)
    echo.
    pause
)

echo Zapuskayutsya vse komponenti:
echo   - HTTP server ^(port 8080^)
echo   - Parser YouTube chata ^(s OAuth^)
echo   - GUI dlya nastroek
echo.

REM Sohranayem absolutniy put k proektu
set PROJECT_DIR=%~dp0
set VENV_PYTHON=%PROJECT_DIR%venv\Scripts\python.exe

echo Virtualnoe okruzhenie: %VENV_PYTHON%
echo.

echo Zapuskayutsya vse komponenti:
echo   - HTTP server ^(port 8080^)
echo   - GUI dlya nastroek
echo.

REM Zapusk HTTP servera cherez venv Python
echo Zapusk HTTP servera...
start "YouTube Chat - HTTP Server" cmd /k "%VENV_PYTHON%" simple_server.py 8080

echo Ozhidanie zapuska servera...
timeout /t 3 /nobreak >nul

REM Zapusk GUI cherez venv Python
echo Zapusk GUI nastroek...
start "YouTube Chat - GUI" cmd /k "%VENV_PYTHON%" chat_gui_simple.py

echo Ozhidanie zapuska GUI...
timeout /t 2 /nobreak >nul

echo Otkritie chata v brauzere...
start "" "http://localhost:8080/vmix_simple.html"

echo.
echo Sistema zapushchena!
echo.
echo Watchdog rabotaet v fone i avtomaticheski ubivaet processi Anaconda.
echo.
echo.
echo Chto delat dalshe:
echo   1. V GUI vvedite URL YouTube translyacii
echo   2. Nazhmite "Zapustit parser" v GUI
echo   3. Ispolzuyte http://localhost:8080/vmix_simple.html v vMix
echo.
goto END

:SERVER_ONLY
echo.
echo ==========================================
echo        ZAPUSK VEB-SERVERA
echo ==========================================
echo.

REM Absolutniy put k proektu
set PROJECT_DIR=%~dp0
set VENV_PYTHON=%PROJECT_DIR%venv\Scripts\python.exe

echo Virtualnoe okruzhenie aktivirovano
echo Zapusk HTTP servera na portu 8080...
echo.
echo Dostupnie ssilki:
echo   vMix chat: http://localhost:8080/vmix_simple.html
echo   Soobshcheniya JSON: http://localhost:8080/messages.json
echo.
echo Dlya ostanovki nazhmite Ctrl+C
echo.

"%VENV_PYTHON%" simple_server.py 8080
goto END

:GUI_ONLY
echo.
echo ==========================================
echo        ZAPUSK GUI NASTROEK
echo ==========================================
echo.

REM Absolutniy put k proektu
set PROJECT_DIR=%~dp0
set VENV_PYTHON=%PROJECT_DIR%venv\Scripts\python.exe

echo Virtualnoe okruzhenie aktivirovano
echo Zapusk GUI nastroek...
echo.

"%VENV_PYTHON%" chat_gui_simple.py
goto END

:OPEN_BROWSER
echo.
echo Otkritie chata v brauzere...
start "" "http://localhost:8080/vmix_simple.html"
goto END

:CHECK_PARSERS
echo.
echo ==========================================
echo      PROVERKA ZAPUSHCHENNIH PROCESSOV
echo ==========================================

:RESET_SETTINGS
echo.
echo ==========================================
echo      SBROS NASTROEK CHATA
echo ==========================================
echo.
echo VNIMANIE: Etot skript sozdayet rezervnuyu
echo kopiyu i ochishchaet vash fayl nastroek
echo (chat_settings.json).
echo.
call "%PROJECT_DIR%RESET_SETTINGS.bat"
goto END

:KILL_ALL
echo.
echo ==========================================
echo      OSTANOVKA VSEH PROCESSOV
echo ==========================================
echo.
call "%PROJECT_DIR%KILL_ALL_PARSERS.bat"
goto END

:EXIT
echo.
echo Do svidaniya!
exit /b 0

:END
echo.
echo Nazhmite lubuyu klavishu dlya vozvrata v menyu...
pause >nul
goto MENU