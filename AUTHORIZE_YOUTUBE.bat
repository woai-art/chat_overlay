@echo off
chcp 65001 > nul
echo ============================================================
echo   YouTube OAuth Authorization
echo   Авторизация YouTube для парсера чата
echo ============================================================
echo.
echo Этот скрипт откроет браузер для авторизации.
echo Вам нужно:
echo   1. Войти в свой аккаунт YouTube
echo   2. Разрешить доступ к чатам
echo   3. После успешной авторизации можете закрыть браузер
echo.
pause

cd /d "%~dp0"
call venv\Scripts\activate.bat
python youtube_auth.py

pause

