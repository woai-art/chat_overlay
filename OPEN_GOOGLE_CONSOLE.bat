@echo off
chcp 65001 > nul
echo ============================================================
echo   Открытие Google Cloud Console
echo   для создания OAuth Credentials
echo ============================================================
echo.
echo Сейчас откроется браузер с Google Cloud Console.
echo.
echo 📋 Следуйте инструкции в файле: GOOGLE_OAUTH_SETUP.md
echo.
echo Кратко:
echo   1. Создайте новый проект "YouTube Chat Parser"
echo   2. Включите YouTube Data API v3
echo   3. Настройте OAuth Consent Screen
echo   4. Создайте OAuth Client ID (Desktop app)
echo   5. Скачайте JSON как "client_secret.json"
echo.
pause

echo.
echo 🌐 Открытие Google Cloud Console...
start "" "https://console.cloud.google.com/"

echo.
echo 📖 Открытие инструкции...
start "" "GOOGLE_OAUTH_SETUP.md"

echo.
echo ✅ Браузер открыт!
echo.
pause


