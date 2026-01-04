@echo off
chcp 65001 > nul
echo ============================================================
echo   Ochistka kesha soobshcheniy
echo ============================================================
echo.
echo Budut ochistcheni:
echo   - Vse fayly temp_messages_*.json
echo   - messages.json
echo   - last_stream_url.txt
echo.
set /p confirm="Prodolzhit? (y/n): "

if /i not "%confirm%"=="y" (
    echo Otmena.
    pause
    exit /b 0
)

echo.
echo Ochistka...

REM Ochischaem vse temp_messages fayly
for %%f in (temp_messages*.json) do (
    echo [] > "%%f"
    echo   Ochistchen: %%f
)

REM Ochischaem osnovnoy fayl soobshcheniy
echo [] > messages.json
echo   Ochistchen: messages.json

REM Ochischaem URL poslednogo strima
echo. > last_stream_url.txt
echo   Ochistchen: last_stream_url.txt

echo.
echo ============================================================
echo   Kesh uspeshno ochistchen!
echo ============================================================
echo.
echo Teper mozhno zapuskat parser dlya novoy translyacii.
echo.
pause

