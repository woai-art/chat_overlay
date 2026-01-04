@echo off
chcp 65001 > nul
cls
echo ============================================================
echo   EKSTRENNAYA OSTANOVKA VSEH PARSEROV
echo ============================================================
echo.
echo VNIMANIE! Budet ostanovleno:
echo   - Vse processi Python
echo   - Vse parseri chata
echo   - Vse HTTP serveri
echo   - Vse GUI
echo.
set /p confirm="Prodolzhit? (y/n): "

if /i not "%confirm%"=="y" (
    echo Otmena.
    pause
    exit /b 0
)

echo.
echo ============================================================
echo Ostanovka vseh processov Python...
echo ============================================================
echo.

REM Ostanovka po nazvaniyam okon
echo [1] Ostanovka po nazvaniyam okon...
taskkill /F /FI "WINDOWTITLE eq *YouTube Chat*" 2>nul
taskkill /F /FI "WINDOWTITLE eq *Parser*" 2>nul
taskkill /F /FI "WINDOWTITLE eq *Chat*" 2>nul

echo.
echo [2] Ostanovka HTTP serverov...
taskkill /F /FI "WINDOWTITLE eq *HTTP Server*" 2>nul

echo.
echo [3] Ostanovka VSEH processov python.exe...
taskkill /F /IM python.exe 2>nul

echo.
echo [4] Ostanovka pythonw.exe (fonovie processi)...
taskkill /F /IM pythonw.exe 2>nul

echo.
echo ============================================================
echo Ozhidanie 3 sekundi...
timeout /t 3 /nobreak >nul

echo.
echo ============================================================
echo Proverka - ostalis li processi Python?
echo ============================================================
echo.

tasklist | findstr /i "python.exe"
if errorlevel 1 (
    echo.
    echo ============================================================
    echo   VSE PROCESSI USPESHNO OSTANOVLENI!
    echo ============================================================
    echo.
    echo Teper mozhno zapuskat parser zanovo:
    echo   START.bat -^> opciya 1
    echo.
) else (
    echo.
    echo ============================================================
    echo   VNIMANIE: Nekotorie processi eshche rabotayut!
    echo ============================================================
    echo.
    echo Poprobuite:
    echo   1. Zakrit vse okna vручnuyu
    echo   2. Perezagruzit kompyuter
    echo.
)

echo ============================================================
echo.
pause





