#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Chat Parser с поддержкой OAuth
"""

import sys
import os
import json
import time
import argparse
import logging
from datetime import datetime
from emoji_database import convert_emojis, get_emoji_count

# =============================================================================
# ЛОГИРОВАНИЕ
# =============================================================================
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file = 'parser.log'
log_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)

logger = logging.getLogger('chat_parser')
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

# =============================================================================

def load_settings():
    """Загружает настройки из файла"""
    try:
        with open('chat_settings.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Не удалось загрузить chat_settings.json: {e}")
        return {}

def load_oauth_tokens():
    """Загружает OAuth токены"""
    token_file = 'youtube_oauth_token.json'
    if os.path.exists(token_file):
        try:
            with open(token_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка чтения токенов: {e}")
            return None
    return None

def load_client_secrets():
    """Загружает client credentials из файла"""
    client_secret_file = 'client_secret.json'
    
    if not os.path.exists(client_secret_file):
        logger.error(f"❌ Файл {client_secret_file} не найден!")
        logger.error("Запустите OAuth авторизацию: AUTHORIZE_YOUTUBE.bat")
        return None, None
    
    try:
        with open(client_secret_file, 'r', encoding='utf-8') as f:
            credentials = json.load(f)
        
        if 'installed' in credentials:
            client_data = credentials['installed']
        elif 'web' in credentials:
            client_data = credentials['web']
        else:
            return None, None
        
        return client_data.get('client_id'), client_data.get('client_secret')
    except Exception as e:
        logger.error(f"Ошибка чтения credentials: {e}")
        return None, None

def refresh_access_token(refresh_token):
    """Обновляет access token"""
    import requests
    
    # Загружаем credentials из файла
    client_id, client_secret = load_client_secrets()
    
    if not client_id or not client_secret:
        raise Exception("Не удалось загрузить client credentials")
    
    token_url = 'https://oauth2.googleapis.com/token'
    
    data = {
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token'
    }
    
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        tokens = response.json()
        # Сохраняем обновленные токены
        tokens['refresh_token'] = refresh_token  # Сохраняем refresh_token
        with open('youtube_oauth_token.json', 'w', encoding='utf-8') as f:
            json.dump(tokens, f, indent=2)
        return tokens
    else:
        raise Exception(f"Ошибка обновления токена: {response.text}")

def load_last_url():
    """Загружает последний URL трансляции"""
    try:
        with open('last_stream_url.txt', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        return None

def save_last_url(url):
    """Сохраняет URL трансляции"""
    try:
        with open('last_stream_url.txt', 'w', encoding='utf-8') as f:
            f.write(url)
    except Exception as e:
        logger.error(f"Не удалось сохранить last_stream_url.txt: {e}")

def clear_old_messages(filename='messages.json'):
    """Очищает старые сообщения"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Не удалось очистить {filename}: {e}")

def process_emojis(text):
    """Обрабатывает эмоджи в тексте и удаляет inline-стили"""
    import re
    result = convert_emojis(text, performance_mode='channel')
    
    # АГРЕССИВНО удаляем inline-стили из всех <img> тегов
    result = re.sub(r'\s+style="[^"]*"', '', result)
    result = re.sub(r'\s+width="[^"]*"', '', result)
    result = re.sub(r'\s+height="[^"]*"', '', result)
    
    return result

def load_existing_messages(filename='messages.json'):
    """Загружает существующие сообщения"""
    messages = []
    seen_ids = set()
    if not os.path.exists(filename):
        return messages, seen_ids

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    message_id = item.get('id')
                    if message_id and message_id not in seen_ids:
                        messages.append(item)
                        seen_ids.add(message_id)
    except Exception as e:
        logger.error(f"Не удалось загрузить существующие сообщения из {filename}: {e}")

    return messages, seen_ids

def save_messages(messages, filename='messages.json', max_retries=10):
    """Сохраняет сообщения в JSON файл"""
    try:
        for attempt in range(1, max_retries + 1):
            try:
                temp_filename = f"{filename}.tmp.{os.getpid()}.{attempt}"
                with open(temp_filename, 'w', encoding='utf-8') as f:
                    json.dump(messages, f, ensure_ascii=False, indent=2)
                
                try:
                    os.replace(temp_filename, filename)
                except PermissionError:
                    if attempt == max_retries:
                        raise
                    if os.path.exists(temp_filename):
                        try:
                            os.remove(temp_filename)
                        except Exception:
                            pass
                    time.sleep(0.2 * attempt)
                    continue
                break
            except Exception as inner:
                if attempt == max_retries:
                    logger.warning(f"⚠️ Не удалось сохранить {filename} атомарно (попытка {attempt}/{max_retries}): {inner}")
                    try:
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(messages, f, ensure_ascii=False, indent=2)
                        return
                    except Exception as fallback_error:
                        raise fallback_error
                else:
                    time.sleep(0.2 * attempt)
    except Exception as e:
        logger.error(f"Не удалось сохранить сообщения в {filename}: {e}")

def write_status(status):
    """Записывает статус в файл"""
    try:
        with open('parser_status.txt', 'w', encoding='utf-8') as f:
            f.write(status)
    except Exception as e:
        logger.error(f"Не удалось записать статус: {e}")

def extract_video_id(url):
    """Извлекает video ID из URL"""
    import re
    
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
        r'(?:live\/)([0-9A-Za-z_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    if len(url) == 11 and re.match(r'^[0-9A-Za-z_-]{11}$', url):
        return url
    
    return None

def main():
    parser = argparse.ArgumentParser(description='YouTube Chat Parser (OAuth)')
    parser.add_argument('video_url', nargs='?', help='URL трансляции YouTube')
    parser.add_argument('--output', '-o', default='messages.json', help='Файл для сохранения сообщений')
    parser.add_argument('--interval', '-i', type=float, help='Интервал обновления в секундах')
    parser.add_argument('--clear', '-c', action='store_true', help='Очистить старые сообщения')
    
    args = parser.parse_args()
    
    logger.info("Парсер запущен (OAuth).")
    
    # Проверяем наличие OAuth токенов
    tokens = load_oauth_tokens()
    if not tokens:
        write_status("ERROR: No OAuth")
        logger.error("=" * 60)
        logger.error("НЕТ OAUTH АВТОРИЗАЦИИ!")
        logger.error("=" * 60)
        logger.error("Для работы парсера нужна OAuth авторизация YouTube.")
        logger.error("")
        logger.error("Запустите файл: AUTHORIZE_YOUTUBE.bat")
        logger.error("")
        logger.error("Или выполните команду:")
        logger.error("  python youtube_auth.py")
        logger.error("=" * 60)
        return
    
    logger.info("✅ OAuth токены найдены")
    
    # Получаем URL
    video_url = args.video_url
    if not video_url:
        settings = load_settings()
        video_url = settings.get('video_url', '')
    
    if not video_url:
        write_status("ERROR: No URL")
        logger.error("URL трансляции не указан.")
        return
    
    # Извлекаем video ID
    video_id = extract_video_id(video_url)
    if not video_id:
        write_status("ERROR: Invalid URL")
        logger.error(f"Не удалось извлечь video ID из URL: {video_url}")
        return
    
    logger.info(f"URL трансляции: {video_url}")
    logger.info(f"Video ID: {video_id}")
    logger.info(f"Загружено эмоджи: {get_emoji_count()}")
    
    # Проверяем изменение URL
    last_url = load_last_url()
    if last_url != video_url:
        logger.info("Обнаружен новый URL, очистка старых сообщений.")
        clear_old_messages(args.output)
        save_last_url(video_url)
    elif args.clear:
        logger.info("Принудительная очистка старых сообщений.")
        clear_old_messages(args.output)
    
    # Загружаем настройки
    settings = load_settings()
    update_interval = args.interval or settings.get('update_interval', 2)
    max_messages = settings.get('max_messages', 20)
    
    write_status("CONNECTING")
    logger.info("Подключение к чату...")
    
    messages, seen_message_ids = load_existing_messages(args.output)
    
    try:
        from chat_downloader import ChatDownloader
        
        # Создаем YouTube URL
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Обновляем access token если нужно
        if 'refresh_token' in tokens:
            try:
                tokens = refresh_access_token(tokens['refresh_token'])
                logger.info("✅ Access token обновлен")
            except Exception as e:
                logger.warning(f"Не удалось обновить токен: {e}")
        
        # Подключаемся к чату с OAuth
        access_token = tokens.get('access_token')
        
        logger.info("Создание ChatDownloader с OAuth...")
        chat_downloader = ChatDownloader()
        
        # Получаем чат
        chat = chat_downloader.get_chat(
            youtube_url,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        write_status("CONNECTED")
        logger.info("✅ Успешно подключено к чату с OAuth")
        
        # Основной цикл
        for message in chat:
            try:
                author_name = message.get('author', {}).get('name', 'Unknown')
                message_text = message.get('message', '')
                message_id = message.get('message_id', f"{int(time.time() * 1000)}_{author_name}")
                timestamp = int(message.get('timestamp', time.time() * 1000))
                
                # Пропускаем дубликаты
                if message_id in seen_message_ids:
                    continue
                
                # Обрабатываем эмоджи
                processed_text = process_emojis(message_text) if message_text else ""
                
                # Формируем объект сообщения
                message_obj = {
                    'id': message_id,
                    'text': processed_text,
                    'author': {
                        'name': author_name,
                        'avatar': message.get('author', {}).get('images', [{}])[0].get('url', 'https://via.placeholder.com/32x32?text=👤'),
                        'is_sponsor': message.get('author', {}).get('is_verified', False),
                        'is_moderator': message.get('author', {}).get('is_moderator', False),
                        'is_owner': message.get('author', {}).get('is_owner', False),
                        'badges': message.get('author', {}).get('badges', [])
                    },
                    'timestamp': timestamp
                }
                
                messages.append(message_obj)
                seen_message_ids.add(message_id)
                
                # Ограничиваем количество
                if len(messages) > max_messages:
                    overflow = len(messages) - max_messages
                    for _ in range(overflow):
                        removed = messages.pop(0)
                        removed_id = removed.get('id')
                        if removed_id:
                            seen_message_ids.discard(removed_id)
                
                # Сохраняем
                save_messages(messages, args.output)
                write_status(f"RUNNING: {len(messages)} messages")
                
            except Exception as e:
                logger.error(f"Ошибка обработки сообщения: {e}")
                continue
        
    except KeyboardInterrupt:
        write_status("STOPPED")
        logger.info("Парсер остановлен пользователем.")
    except Exception as e:
        error_message = f"ERROR: {str(e)}"
        write_status(error_message)
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)
    finally:
        if messages:
            save_messages(messages, args.output)
        write_status("FINISHED")
        logger.info("Парсер завершил работу.")

if __name__ == "__main__":
    while True:
        try:
            main()
            logger.info("Парсер завершился. Перезапуск через 10 секунд...")
            time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Получен сигнал остановки.")
            break
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}. Перезапуск через 30 секунд...")
            time.sleep(30)

