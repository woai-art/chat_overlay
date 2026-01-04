@echo off
chcp 65001 > nul
cls
echo ============================================================
echo   PROVERKA ZAPUSHCHENNIH PARSEROV
echo ============================================================
echo.

echo [1] Poisk processov Python...
echo.
tasklist /FI "IMAGENAME eq python.exe" | findstr /i "python.exe"
if errorlevel 1 (
    echo    Net zapushchennih processov Python
) else (
    echo    ^ Naydeni processi Python
)

echo.
echo ============================================================
echo [2] Poisk okon s parserom chata...
echo.

REM Ishchem okna s nazvaniem parser
tasklist /FI "WINDOWTITLE eq *Parser*" /V 2>nul | findstr /v "INFO:"
tasklist /FI "WINDOWTITLE eq *Chat*" /V 2>nul | findstr /v "INFO:"

echo.
echo ============================================================
echo [3] Podrobnaya informaciya o processah Python...
echo.

REM Pokazivaem vse Python processi s komandnoy strokoy
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | ForEach-Object { Write-Host \"PID: $($_.Id) - $($_.MainWindowTitle)\"; $cmd = (Get-WmiObject Win32_Process -Filter \"ProcessId=$($_.Id)\").CommandLine; if ($cmd -match 'chat_parser') { Write-Host \"  [PARSER!] $cmd\" -ForegroundColor Yellow } else { Write-Host \"  $cmd\" -ForegroundColor Gray } }"

echo.
echo ============================================================
echo.
echo CHTO DELAT ESLI VIDITE NESKOLKO PARSEROV:
echo.
echo   1. Zapustite START.bat
echo   2. Viberite opciyu 8 - Ostanovit vse processi
echo   3. Proverte eshche raz etim skriptom
echo   4. Zapustite parser zanovo
echo.
echo ============================================================
echo.
pause
