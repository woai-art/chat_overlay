#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube OAuth Authentication Tool
Инструмент для OAuth аутентификации YouTube
"""

import os
import sys
import json
import logging
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# OAuth credentials (загружаются из client_secret.json)
CLIENT_SECRET_FILE = 'client_secret.json'
REDIRECT_URI = 'http://localhost:8090/oauth2callback'
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly', 
          'https://www.googleapis.com/auth/youtube.force-ssl']

def load_client_secrets():
    """Загружает credentials из client_secret.json"""
    if not os.path.exists(CLIENT_SECRET_FILE):
        logger.error("=" * 60)
        logger.error("❌ ФАЙЛ client_secret.json НЕ НАЙДЕН!")
        logger.error("=" * 60)
        logger.error("")
        logger.error("Для работы OAuth нужен файл с вашими Google credentials.")
        logger.error("")
        logger.error("📋 Следуйте инструкции в файле: GOOGLE_OAUTH_SETUP.md")
        logger.error("")
        logger.error("Кратко:")
        logger.error("1. Откройте: https://console.cloud.google.com/")
        logger.error("2. Создайте новый проект")
        logger.error("3. Включите YouTube Data API v3")
        logger.error("4. Создайте OAuth 2.0 Client ID (Desktop app)")
        logger.error("5. Скачайте JSON файл как 'client_secret.json'")
        logger.error("6. Поместите его в папку:")
        logger.error(f"   {os.path.abspath('.')}")
        logger.error("")
        logger.error("=" * 60)
        return None, None
    
    try:
        with open(CLIENT_SECRET_FILE, 'r', encoding='utf-8') as f:
            credentials = json.load(f)
        
        # Поддержка обоих форматов (installed / web)
        if 'installed' in credentials:
            client_data = credentials['installed']
        elif 'web' in credentials:
            client_data = credentials['web']
        else:
            logger.error("❌ Неверный формат client_secret.json")
            return None, None
        
        client_id = client_data.get('client_id')
        client_secret = client_data.get('client_secret')
        
        if not client_id or not client_secret:
            logger.error("❌ client_secret.json не содержит client_id или client_secret")
            return None, None
        
        logger.info(f"✅ Credentials загружены из {CLIENT_SECRET_FILE}")
        return client_id, client_secret
        
    except Exception as e:
        logger.error(f"❌ Ошибка чтения {CLIENT_SECRET_FILE}: {e}")
        return None, None

# Файл для хранения токенов
TOKEN_FILE = 'youtube_oauth_token.json'

# Глобальная переменная для хранения кода авторизации
auth_code = None
auth_event = threading.Event()

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Обработчик callback для OAuth"""
    
    def log_message(self, format, *args):
        """Отключаем логирование HTTP сервера"""
        pass
    
    def do_GET(self):
        """Обрабатываем GET запрос от OAuth callback"""
        global auth_code
        
        # Парсим URL
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        
        if 'code' in params:
            auth_code = params['code'][0]
            
            # Отправляем успешный ответ
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Успешная авторизация</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    }
                    .container {
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        text-align: center;
                    }
                    h1 { color: #4CAF50; margin-bottom: 20px; }
                    p { color: #666; font-size: 18px; }
                    .checkmark {
                        width: 80px;
                        height: 80px;
                        border-radius: 50%;
                        display: block;
                        stroke-width: 2;
                        stroke: #4CAF50;
                        stroke-miterlimit: 10;
                        margin: 20px auto;
                        animation: fill .4s ease-in-out .4s forwards, scale .3s ease-in-out .9s both;
                    }
                    @keyframes fill {
                        100% { box-shadow: inset 0px 0px 0px 40px #4CAF50; }
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="checkmark">
                        <svg viewBox="0 0 52 52">
                            <circle cx="26" cy="26" r="25" fill="none"/>
                            <path fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8" stroke="#4CAF50" stroke-width="3"/>
                        </svg>
                    </div>
                    <h1>✅ Авторизация успешна!</h1>
                    <p>Вы успешно привязали аккаунт YouTube.</p>
                    <p>Теперь можете закрыть это окно и вернуться к парсеру.</p>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode('utf-8'))
            auth_event.set()
            
        elif 'error' in params:
            # Отправляем ответ об ошибке
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            error = params['error'][0]
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Ошибка авторизации</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background: #f44336;
                    }}
                    .container {{
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        text-align: center;
                    }}
                    h1 {{ color: #f44336; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>❌ Ошибка авторизации</h1>
                    <p>Ошибка: {error}</p>
                    <p>Попробуйте снова.</p>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode('utf-8'))
            auth_event.set()

def get_authorization_url(client_id):
    """Генерирует URL для авторизации"""
    from urllib.parse import urlencode
    
    params = {
        'client_id': client_id,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(SCOPES),
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urlencode(params)
    return auth_url

def exchange_code_for_tokens(code, client_id, client_secret):
    """Обменивает код авторизации на токены"""
    import requests
    
    token_url = 'https://oauth2.googleapis.com/token'
    
    data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Ошибка получения токенов: {response.text}")

def save_tokens(tokens):
    """Сохраняет токены в файл"""
    with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(tokens, f, indent=2)
    logger.info(f"✅ Токены сохранены в {TOKEN_FILE}")

def load_tokens():
    """Загружает токены из файла"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def refresh_access_token(refresh_token, client_id, client_secret):
    """Обновляет access token используя refresh token"""
    import requests
    
    token_url = 'https://oauth2.googleapis.com/token'
    
    data = {
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token'
    }
    
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Ошибка обновления токена: {response.text}")

def main():
    global auth_code
    
    logger.info("=" * 60)
    logger.info("YouTube OAuth Authentication")
    logger.info("Привязка аккаунта YouTube к парсеру")
    logger.info("=" * 60)
    logger.info("")
    
    # Загружаем client credentials
    logger.info("📋 Загрузка OAuth credentials...")
    client_id, client_secret = load_client_secrets()
    
    if not client_id or not client_secret:
        logger.error("")
        logger.error("⚠️  Откройте файл GOOGLE_OAUTH_SETUP.md для подробной инструкции")
        return 1
    
    logger.info("")
    
    # Проверяем, есть ли уже сохраненные токены
    existing_tokens = load_tokens()
    if existing_tokens:
        logger.info("✅ Найдены существующие токены авторизации")
        logger.info("")
        response = input("Хотите перезаписать их? (y/n): ").lower().strip()
        if response != 'y':
            logger.info("Авторизация отменена")
            return 0
        logger.info("")
    
    # Запускаем локальный HTTP сервер для callback
    logger.info("📡 Запуск локального сервера для OAuth callback...")
    server = HTTPServer(('localhost', 8090), OAuthCallbackHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    logger.info("✅ Сервер запущен на http://localhost:8090")
    logger.info("")
    
    # Генерируем URL авторизации
    auth_url = get_authorization_url(client_id)
    
    logger.info("🌐 Открываем браузер для авторизации...")
    logger.info("")
    logger.info("Если браузер не открылся автоматически, откройте эту ссылку:")
    logger.info(auth_url)
    logger.info("")
    
    # Открываем браузер
    webbrowser.open(auth_url)
    
    logger.info("⏳ Ожидание авторизации...")
    logger.info("   (Войдите в свой аккаунт YouTube и разрешите доступ)")
    logger.info("")
    
    # Ждем получения кода авторизации
    auth_event.wait(timeout=300)  # 5 минут
    
    server.shutdown()
    
    if not auth_code:
        logger.error("❌ Не получен код авторизации (таймаут или отказ)")
        return 1
    
    logger.info("✅ Код авторизации получен")
    logger.info("")
    
    # Обмениваем код на токены
    logger.info("🔄 Обмен кода на токены доступа...")
    try:
        tokens = exchange_code_for_tokens(auth_code, client_id, client_secret)
        logger.info("✅ Токены успешно получены")
        logger.info("")
        
        # Сохраняем токены
        save_tokens(tokens)
        
        logger.info("=" * 60)
        logger.info("✅ УСПЕХ! Аккаунт YouTube успешно привязан к парсеру")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Теперь парсер будет использовать ваш аккаунт для")
        logger.info("доступа к чатам YouTube трансляций.")
        logger.info("")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        
        input("\nНажмите Enter для выхода...")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        logger.info("\n\nПрервано пользователем")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\n❌ Неожиданная ошибка: {e}", exc_info=True)
        input("\nНажмите Enter для выхода...")
        sys.exit(1)

