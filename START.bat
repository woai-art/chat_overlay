@echo off
chcp 65001 >nul
cd /d "%~dp0"

:MENU
cls
echo.
echo ==========================================
echo     🎬 YOUTUBE CHAT ДЛЯ VMIX
echo ==========================================
echo.
echo Выберите действие:
echo.
echo   1. 🚀 Полный запуск (Сервер + Парсер + GUI)
echo   2. 🌐 Только веб-сервер
echo   3. 🎨 Демонстрация тем
echo   4. 🔧 Только GUI настроек
echo   5. 🎭 Тест спонсоров (симуляция)
echo   6. 📺 Открыть чат в браузере
echo   7. 🛑 Остановить все процессы
echo   8. ❌ Выход
echo.
echo ==========================================
echo.
set /p choice="Введите номер (1-8): "

if "%choice%"=="1" goto FULL_START
if "%choice%"=="2" goto SERVER_ONLY
if "%choice%"=="3" goto THEME_DEMO
if "%choice%"=="4" goto GUI_ONLY
if "%choice%"=="5" goto TEST_SPONSORS
if "%choice%"=="6" goto OPEN_CHAT
if "%choice%"=="7" goto STOP_ALL
if "%choice%"=="8" goto EXIT

echo.
echo ❌ Неверный выбор. Попробуйте снова.
timeout /t 2 /nobreak >nul
goto MENU

:FULL_START
echo.
echo ==========================================
echo      🚀 ПОЛНЫЙ ЗАПУСК СИСТЕМЫ
echo ==========================================
echo.
echo Запускаются все компоненты:
echo   - HTTP сервер (порт 8080)
echo   - Парсер YouTube чата
echo   - GUI для настроек
echo   - Автоматически откроется чат в браузере
echo.

call venv\Scripts\activate.bat

echo ✅ Виртуальное окружение активировано
echo.

echo 🌐 Запуск HTTP сервера...
start "YouTube Chat - HTTP Server" cmd /k "python simple_server.py 8080"

echo ⏳ Ожидание запуска сервера...
timeout /t 3 /nobreak >nul

echo 🔧 Запуск GUI настроек...
start "YouTube Chat - GUI" cmd /k "python chat_gui_simple.py"

echo ⏳ Ожидание запуска GUI...
timeout /t 2 /nobreak >nul

echo 🌐 Открытие чата в браузере...
start "" "http://localhost:8080/vmix_simple.html"

echo.
echo ✅ Система запущена!
echo.
echo 📋 Что делать дальше:
echo   1. В GUI введите URL YouTube трансляции
echo   2. Нажмите "Запустить парсер" в GUI
echo   3. Используйте http://localhost:8080/vmix_simple.html в vMix
echo.
echo 🎨 Смена тем: Ctrl+T в чате или кнопка "🎨"
echo   5 красивых тем: Барби, Киберпанк, Минимализм, Темная, Ретро
echo.
goto END

:SERVER_ONLY
echo.
echo ==========================================
echo        🌐 ЗАПУСК ВЕБА-СЕРВЕРА
echo ==========================================
echo.

call venv\Scripts\activate.bat

echo ✅ Виртуальное окружение активировано
echo 🌐 Запуск HTTP сервера на порту 8080...
echo.
echo Доступные ссылки:
echo   📺 vMix чат (Premium): http://localhost:8080/vmix_simple.html
echo   📝 Сообщения (JSON):   http://localhost:8080/messages.json
echo   ⚙️ Настройки:          http://localhost:8080/chat_settings.json
echo.
echo Для остановки нажмите Ctrl+C
echo.

python simple_server.py 8080
goto END

:THEME_DEMO
echo.
echo ==========================================
echo        🎨 ДЕМОНСТРАЦИЯ ТЕМ
echo ==========================================
echo.

call venv\Scripts\activate.bat

echo ✅ Виртуальное окружение активировано
echo 🌐 Запуск HTTP сервера...

start "HTTP Server" cmd /c "python simple_server.py 8080"

echo ⏳ Ожидание запуска сервера...
timeout /t 3 /nobreak >nul

echo 🎨 Открытие демонстрации тем...
start "" "http://localhost:8080/theme_demo.html"

echo.
echo ✅ Демонстрация тем запущена!
echo.
echo 🎮 Горячие клавиши:
echo   Ctrl + T     - Селектор тем
echo   Ctrl + ←/→   - Переключение тем
echo   Клик по теме - Применить тему
echo.
goto END

:GUI_ONLY
echo.
echo ==========================================
echo        🔧 ЗАПУСК GUI НАСТРОЕК
echo ==========================================
echo.

call venv\Scripts\activate.bat

echo ✅ Виртуальное окружение активировано
echo 🔧 Запуск GUI настроек...
echo.

python chat_gui_simple.py
goto END

:TEST_SPONSORS
echo.
echo ==========================================
echo      🎭 ТЕСТ СПОНСОРОВ (СИМУЛЯЦИЯ)
echo ==========================================
echo.

call venv\Scripts\activate.bat

echo ✅ Виртуальное окружение активировано
echo 🌐 Запуск HTTP сервера...

start "HTTP Server" cmd /c "python simple_server.py 8080"

echo ⏳ Ожидание запуска сервера...
timeout /t 3 /nobreak >nul

echo 🎭 Запуск симулятора спонсоров...
echo 📊 Будет создано примерно 12 сообщений в минуту
echo.

python simulate_sponsors.py 60 12

echo.
echo ✅ Симуляция завершена!
echo 🌐 Откройте http://localhost:8080/chat_local.html для просмотра
echo.
goto END

:OPEN_CHAT
echo.
echo ==========================================
echo        📺 ОТКРЫТИЕ ЧАТА В БРАУЗЕРЕ
echo ==========================================
echo.

echo 🌐 Открытие основного чата...
start "" "http://localhost:8080/chat_local.html"

echo ✅ Чат открыт в браузере!
echo.
echo 💡 Если страница не загружается:
echo   1. Запустите сначала веб-сервер (опция 2)
echo   2. Проверьте, что порт 8080 свободен
echo.
goto END

:STOP_ALL
echo.
echo ==========================================
echo        🛑 ОСТАНОВКА ВСЕХ ПРОЦЕССОВ
echo ==========================================
echo.

echo 🔍 Поиск и остановка процессов YouTube Chat...

taskkill /f /fi "WINDOWTITLE eq YouTube Chat - HTTP Server" 2>nul
taskkill /f /fi "WINDOWTITLE eq YouTube Chat - GUI" 2>nul
taskkill /f /fi "WINDOWTITLE eq YouTube Chat - Parser" 2>nul
taskkill /f /fi "WINDOWTITLE eq HTTP Server" 2>nul

echo ✅ Все процессы остановлены!
echo.
goto END

:EXIT
echo.
echo 👋 До свидания!
exit /b 0

:END
echo.
echo Нажмите любую клавишу для возврата в меню...
pause >nul
goto MENU 