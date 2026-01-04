@echo off
echo ============================================================
echo   OCHISTKA I SBROS NASTROEK (chat_settings.json)
echo ============================================================
echo.

set "SETTINGS_FILE=chat_settings.json"

if exist "%SETTINGS_FILE%" (
    echo Nayden fayl nastroek: %SETTINGS_FILE%
    echo Sozdanie rezervnoy kopii...
    copy "%SETTINGS_FILE%" "%SETTINGS_FILE%.bak"
    echo.
    echo Ochistka fayla nastroek...
    echo {} > "%SETTINGS_FILE%"
    echo.
    echo ============================================================
    echo   [OK] Fayl nastroek ochishchen!
    echo ============================================================
    echo.
    echo Stariye nastroyki sohraneni v: %SETTINGS_FILE%.bak
    echo.
) else (
    echo Fayl nastroek %SETTINGS_FILE% ne nayden.
    echo Sozdanie novogo fayla...
    echo {} > "%SETTINGS_FILE%"
    echo.
    echo ============================================================
    echo   [OK] Novyy fayl nastroek sozdan!
    echo ============================================================
    echo.
)

pause



