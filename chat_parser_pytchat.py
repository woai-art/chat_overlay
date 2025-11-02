#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import pytchat
import json
import time
import argparse
import logging
from datetime import datetime

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

# Словарь для замены эмоджи-кодов на символы
emoji_map = {
    ':)': '😊', ':-)': '😊', ':(': '😢', ':-(': '😢',
    ':D': '😄', ':-D': '😄', ':P': '😛', ':-P': '😛',
    ';)': '😉', ';-)': '😉', ':o': '😮', ':-o': '😮',
    ':O': '😱', ':-O': '😱', ':|': '😐', ':-|': '😐',
    ':*': '😘', ':-*': '😘', '<3': '❤️', '</3': '💔',
    ':heart:': '❤️', ':fire:': '🔥', ':thumbsup:': '👍',
    ':thumbsdown:': '👎', ':clap:': '👏', ':wave:': '👋',
    ':eyes:': '👀', ':100:': '💯', ':rocket:': '🚀',
    ':star:': '⭐', ':crown:': '👑', ':gem:': '💎',
}

def load_settings():
    """Загружает настройки из файла"""
    try:
        with open('chat_settings.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Не удалось загрузить chat_settings.json: {e}")
        return {}

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
    """Обрабатывает эмоджи в тексте"""
    if not text:
        return text
        
    result = text
    for emoji_code, emoji_char in emoji_map.items():
        result = result.replace(emoji_code, emoji_char)
    
    return result

def save_messages(messages, filename='messages.json'):
    """Сохраняет сообщения в JSON файл"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Не удалось сохранить сообщения в {filename}: {e}")

def write_status(status):
    """Записывает статус в файл для GUI"""
    try:
        with open('parser_status.txt', 'w', encoding='utf-8') as f:
            f.write(status)
    except Exception as e:
        logger.error(f"Не удалось записать статус в parser_status.txt: {e}")

def extract_video_id(url):
    """Извлекает video ID из различных форматов YouTube URL"""
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
    
    # Если не нашли, может это уже ID?
    if len(url) == 11 and re.match(r'^[0-9A-Za-z_-]{11}$', url):
        return url
    
    return None

def main():
    parser = argparse.ArgumentParser(description='YouTube Chat Parser (PyTChat)')
    parser.add_argument('video_url', nargs='?', help='URL трансляции YouTube')
    parser.add_argument('--output', '-o', default='messages.json', help='Файл для сохранения сообщений')
    parser.add_argument('--interval', '-i', type=float, help='Интервал обновления в секундах')
    parser.add_argument('--clear', '-c', action='store_true', help='Очистить старые сообщения')
    
    args = parser.parse_args()
    
    logger.info("Парсер запущен (PyTChat).")
    
    # Получаем URL из аргументов или настроек
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
    
    # Проверяем, изменился ли URL трансляции
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
    
    messages = []
    
    try:
        # Создаем объект чата PyTChat
        chat = pytchat.create(video_id)
        
        write_status("CONNECTED")
        logger.info("Успешно подключено к чату.")
        
        # Основной цикл чтения сообщений
        while chat.is_alive():
            try:
                # Получаем новые сообщения
                for c in chat.get().sync_items():
                    try:
                        # Формируем объект сообщения в формате совместимом со старым парсером
                        author_name = c.author.name
                        message_text = c.message
                        # Используем текущее время в миллисекундах для совместимости с JavaScript Date.now()
                        timestamp = int(time.time() * 1000)
                        message_id = c.id if hasattr(c, 'id') else f"{timestamp}_{author_name}"
                        
                        # URL аватара
                        avatar_url = c.author.imageUrl if hasattr(c.author, 'imageUrl') else 'https://via.placeholder.com/32x32?text=👤'
                        
                        # Определяем роли пользователя
                        is_sponsor = c.author.isChatSponsor if hasattr(c.author, 'isChatSponsor') else False
                        is_moderator = c.author.isChatModerator if hasattr(c.author, 'isChatModerator') else False
                        is_owner = c.author.isChatOwner if hasattr(c.author, 'isChatOwner') else False
                        
                        # Обрабатываем значки (badges)
                        user_badges = []
                        if hasattr(c.author, 'badgeUrl') and c.author.badgeUrl:
                            badge_type = 'badge'
                            if is_sponsor:
                                badge_type = 'member'
                            elif is_moderator:
                                badge_type = 'moderator'
                            elif is_owner:
                                badge_type = 'owner'
                            
                            user_badges.append({
                                'type': badge_type,
                                'title': badge_type.capitalize(),
                                'icon': c.author.badgeUrl
                            })
                        
                        # Обрабатываем эмоджи
                        processed_text = process_emojis(message_text)
                        
                        message_obj = {
                            'id': message_id,
                            'text': processed_text,
                            'author': {
                                'name': author_name,
                                'avatar': avatar_url,
                                'is_sponsor': is_sponsor,
                                'is_moderator': is_moderator,
                                'is_owner': is_owner,
                                'badges': user_badges
                            },
                            'timestamp': timestamp
                        }
                        
                        messages.append(message_obj)
                        
                        # Ограничиваем количество сообщений
                        if len(messages) > max_messages:
                            messages = messages[-max_messages:]
                        
                        # Сохраняем сообщения
                        save_messages(messages, args.output)
                        
                        write_status(f"RUNNING: {len(messages)} messages")
                        
                        logger.info(f"Новое сообщение от {author_name}: {processed_text[:50]}...")
                        
                    except Exception as e:
                        logger.error(f"Ошибка обработки сообщения: {e}")
                        continue
                
                # Небольшая задержка между проверками
                time.sleep(update_interval)
                
            except KeyboardInterrupt:
                logger.info("Парсер остановлен пользователем (KeyboardInterrupt).")
                break
            except Exception as e:
                logger.error(f"Ошибка в цикле чтения: {e}")
                # Пробуем продолжить работу
                time.sleep(5)
                continue
                
    except KeyboardInterrupt:
        write_status("STOPPED")
        logger.info("Парсер остановлен пользователем.")
    except Exception as e:
        error_message = f"ERROR: {str(e)}"
        write_status(error_message)
        logger.critical(f"Критическая ошибка парсера: {e}", exc_info=True)
    finally:
        if messages:
            save_messages(messages, args.output)
        write_status("FINISHED")
        logger.info("Парсер завершил работу.")

if __name__ == "__main__":
    main()

