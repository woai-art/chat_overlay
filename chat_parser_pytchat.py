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

# Эмоджи теперь обрабатываются через внешнюю базу данных emoji_database.py

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

EMOJI_DEBUGGED_IDS = set()


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
    """
    Загружает существующие сообщения и удаляет дубли по ID.
    Возвращает список сообщений и множество уже обработанных ID.
    """
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

def extract_message_text(chat_item):
    """
    Извлекает текст сообщения из объекта PyTChat, корректно обрабатывая messageEx.
    Предпочитаем читабельные поля (text, emojiText, shortcuts) и избегаем бинарных ID.
    """
    try:
        message_ex = getattr(chat_item, 'messageEx', None)
        if message_ex:
            parts = []
            if isinstance(message_ex, list):
                for item in message_ex:
                    if isinstance(item, dict):
                        # Сначала пробуем получить текстовое представление
                        # Проверяем различные варианты полей: text, txt, emojiText
                        text_value = item.get('text') or item.get('txt') or item.get('emojiText')
                        if text_value:
                            parts.append(text_value)
                            continue

                        shortcuts = item.get('shortcuts')
                        if isinstance(shortcuts, list) and shortcuts:
                            parts.append(shortcuts[0])
                            continue

                        label = item.get('label')
                        if isinstance(label, dict):
                            simple_text = label.get('simpleText')
                            if simple_text:
                                parts.append(simple_text)
                                continue
                            runs = label.get('runs')
                            if isinstance(runs, list):
                                for run in runs:
                                    run_text = run.get('text')
                                    if run_text:
                                        parts.append(run_text)
                        
                        # Если есть emojiId, но нет текста, пробуем получить Unicode эмодзи из emojiText или alt
                        emoji_id = item.get('emojiId')
                        if emoji_id:
                            # Пробуем получить Unicode эмодзи из различных полей
                            emoji_unicode = item.get('emojiText') or item.get('alt') or item.get('text') or item.get('txt')
                            if emoji_unicode:
                                parts.append(emoji_unicode)
                            elif emoji_id not in EMOJI_DEBUGGED_IDS:
                                EMOJI_DEBUGGED_IDS.add(emoji_id)
                                logger.info(f"emoji_debug: messageEx item с emojiId без текста {item}")
                    elif isinstance(item, str):
                        parts.append(item)
            elif isinstance(message_ex, str):
                parts.append(message_ex)

            if not parts:
                logger.info(f"emoji_debug: messageEx без распознанных частей -> {message_ex}")
            else:
                # Если нашли части, объединяем их
                combined = ''.join(parts).strip()
                if combined:
                    return combined
    except Exception as e:
        logger.debug(f"Не удалось полностью разобрать messageEx: {e}", exc_info=True)

    # Фолбэк: обычный текст сообщения
    plain_message = getattr(chat_item, 'message', None)
    if plain_message:
        return plain_message

    # Дополнительный фолбэк: пробуем разобрать JSON
    message_json = getattr(chat_item, 'json', None)
    if message_json:
        try:
            json_data = json.loads(message_json) if isinstance(message_json, str) else message_json
            if isinstance(json_data, dict):
                if 'message' in json_data and json_data['message']:
                    return json_data['message']
                runs = json_data.get('message', {}).get('runs')
                if isinstance(runs, list):
                    return ''.join(run.get('text', '') for run in runs if run.get('text'))
        except Exception:
            pass

    return ""

def save_messages(messages, filename='messages.json', max_retries=10):
    """Сохраняет сообщения в JSON файл атомарно, чтобы избежать чтения частично записанных данных"""
    try:
        for attempt in range(1, max_retries + 1):
            try:
                temp_filename = f"{filename}.tmp.{os.getpid()}.{attempt}"
                with open(temp_filename, 'w', encoding='utf-8') as f:
                    json.dump(messages, f, ensure_ascii=False, indent=2)
                
                try:
                    os.replace(temp_filename, filename)
                except PermissionError:
                    # Файл может быть временно занят vMix или координатором
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
                    logger.warning(f"⚠️ Не удалось сохранить {filename} атомарно (попытка {attempt}/{max_retries}): {inner}. Пробуем прямую запись.")
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
    logger.info(f"Загружено эмоджи: {get_emoji_count()}")
    
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
    
    messages, seen_message_ids = load_existing_messages(args.output)
    if messages:
        # Сохраняем очищенный список (если в исходном файле были дубли)
        save_messages(messages, args.output)
    else:
        seen_message_ids = set()
    
    try:
        # Создаем объект чата PyTChat с поддержкой cookies
        # Пробуем сначала без cookies, если не получится - выведем инструкцию
        try:
            logger.info("Попытка подключения без cookies...")
            chat = pytchat.create(video_id)
        except Exception as e:
            logger.warning(f"Не удалось подключиться без cookies: {e}")
            logger.info("Попытка подключения с cookies из файла...")
            
            # Пробуем загрузить cookies из файла
            cookies_path = 'youtube_cookies.txt'
            if os.path.exists(cookies_path):
                logger.info(f"Найден файл cookies: {cookies_path}")
                chat = pytchat.create(video_id, cookies=cookies_path)
            else:
                logger.error("=" * 60)
                logger.error("ТРЕБУЕТСЯ АУТЕНТИФИКАЦИЯ YOUTUBE!")
                logger.error("=" * 60)
                logger.error("YouTube блокирует доступ к чату без аутентификации.")
                logger.error("")
                logger.error("Для решения проблемы нужно:")
                logger.error("1. Установить расширение 'Get cookies.txt LOCALLY'")
                logger.error("   Chrome: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc")
                logger.error("   Firefox: https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/")
                logger.error("")
                logger.error("2. Открыть youtube.com и войти в свой аккаунт")
                logger.error("3. Экспортировать cookies через расширение")
                logger.error("4. Сохранить файл как 'youtube_cookies.txt' в папку:")
                logger.error(f"   {os.path.abspath('.')}")
                logger.error("=" * 60)
                raise
        
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
                        
                        # Извлекаем текст сообщения (включая эмоджи)
                        message_text = extract_message_text(c)
                        
                        # Логируем сообщения с потенциальными эмодзи для отладки
                        if message_text and any(ord(char) > 0x1F000 for char in message_text[:50]):  # Проверяем на эмодзи в первых 50 символах
                            logger.debug(f"Сообщение с эмодзи от {author_name}: {message_text[:100]}")
                        
                        # Также пробуем получить текст напрямую из message, если messageEx не дал результата
                        if not message_text or len(message_text.strip()) == 0:
                            direct_message = getattr(c, 'message', None)
                            if direct_message and direct_message != message_text:
                                logger.info(f"Фолбэк: используем прямой message для {author_name}: {direct_message[:100]}")
                                message_text = direct_message
                        
                        # Используем текущее время в миллисекундах для совместимости с JavaScript Date.now()
                        timestamp = int(time.time() * 1000)
                        message_id = c.id if hasattr(c, 'id') else f"{timestamp}_{author_name}"

                        # Пропускаем уже сохраненные сообщения
                        if message_id in seen_message_ids:
                            continue
                        
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
                        processed_text = process_emojis(message_text) if message_text else ""
                        
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
                        seen_message_ids.add(message_id)
                        
                        # Ограничиваем количество сообщений
                        if len(messages) > max_messages:
                            overflow = len(messages) - max_messages
                            for _ in range(overflow):
                                removed = messages.pop(0)
                                removed_id = removed.get('id')
                                if removed_id:
                                    seen_message_ids.discard(removed_id)
                        
                        # Сохраняем сообщения
                        save_messages(messages, args.output)
                        
                        write_status(f"RUNNING: {len(messages)} messages")
                        
                        
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
    while True:
        try:
            main()
            logger.info("Парсер завершился нормально. Перезапуск через 10 секунд...")
            time.sleep(10)  # Пауза перед перезапуском
        except KeyboardInterrupt:
            logger.info("Получен сигнал остановки. Завершение работы.")
            break
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}. Перезапуск через 30 секунд...")
            time.sleep(30)  # Более длинная пауза при ошибке

