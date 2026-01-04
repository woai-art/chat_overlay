@echo off
chcp 65001 > nul
title POLNAYA PEREZAGRUZKA SISTEMY

echo.
echo ============================================================
echo   POLNAYA PEREZAGRUZKA SISTEMY CHATA
echo ============================================================
echo.

echo [1/5] Ostanovka vseh processov...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak > nul

echo [2/5] Ochistka kesha i starix soobscheniy...
if exist messages.json del /F /Q messages.json
if exist temp_messages_*.json del /F /Q temp_messages_*.json
if exist last_stream_url.txt del /F /Q last_stream_url.txt

echo [3/5] Sozdanie pustogo messages.json...
echo [] > messages.json

echo [4/5] Ochistka zaversena!
echo.
echo ============================================================
echo   TEPER:
echo   1. Zapustite START.bat
echo   2. V vMix UDALITE browser istochnik
echo   3. Dobavte vmix_simple.html ZANOVO
echo ============================================================
echo.

pause

