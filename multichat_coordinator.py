#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Мульти-чат координатор для YouTube Live Chat
Управляет несколькими парсерами одновременно и объединяет сообщения
"""

import sys
import os
import json
import time
import threading
import logging
import argparse
import subprocess
from datetime import datetime
from queue import Queue, Empty
from emoji_database import convert_emojis, get_emoji_count

# =============================================================================
# ЛОГИРОВАНИЕ
# =============================================================================
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(name)s] %(message)s')
log_file = 'multichat.log'
log_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)

logger = logging.getLogger('multichat_coordinator')
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

# =============================================================================
# МУЛЬТИ-ЧАТ КООРДИНАТОР
# =============================================================================

class MultiChatCoordinator:
    def __init__(self, channels_config, output_file='messages.json', max_messages=50):
        """
        Инициализация мульти-чат координатора
        
        Args:
            channels_config (list): Список конфигураций каналов
            output_file (str): Файл для сохранения объединённых сообщений
            max_messages (int): Максимальное количество сообщений
        """
        self.channels_config = channels_config
        self.output_file = output_file
        self.max_messages = max_messages
        
        # Настройки для высоконагруженных каналов (по умолчанию отключены)
        self.max_messages_per_channel_per_cycle = None  # Без ограничений по умолчанию
        self.message_processing_delay = 0.0  # Без задержек по умолчанию
        self.channel_restart_cooldown = {}  # Кулдаун для перезапуска каналов
        self.performance_optimization_enabled = False  # Флаг оптимизации
        
        # Очереди для сообщений от каждого канала
        self.message_queues = {}
        
        # Процессы парсеров для каждого канала
        self.parser_processes = {}
        
        # Потоки для чтения сообщений от каждого канала
        self.reader_threads = {}
        
        # Общий список сообщений
        self.all_messages = []
        
        # Множество для отслеживания уникальных ID сообщений
        self.seen_message_ids = set()
        
        # Флаг остановки
        self.stop_flag = threading.Event()
        
        # Блокировка для безопасной записи
        self.write_lock = threading.Lock()
        
        # Очередь каналов для перезапуска
        self.restart_queue = set()
        
        logger.info(f"Мульти-чат координатор инициализирован для {len(channels_config)} каналов")
        logger.info(f"Загружено эмоджи: {get_emoji_count()}")
    
    def get_clean_env(self):
        """Возвращает чистое окружение без Anaconda"""
        import copy
        env = copy.copy(os.environ)
        
        # Удаляем Anaconda из PATH
        if 'PATH' in env:
            paths = env['PATH'].split(os.pathsep)
            cleaned_paths = [p for p in paths if 'anaconda' not in p.lower()]
            env['PATH'] = os.pathsep.join(cleaned_paths)
            
            # Добавляем venv в начало PATH
            venv_scripts = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts")
            env['PATH'] = venv_scripts + os.pathsep + env['PATH']
        
        # Удаляем переменные Anaconda
        conda_vars = ['CONDA_DEFAULT_ENV', 'CONDA_PREFIX', 'CONDA_PROMPT_MODIFIER', 
                      'CONDA_SHLVL', 'CONDA_PYTHON_EXE', 'CONDA_EXE']
        for var in conda_vars:
            env.pop(var, None)
        
        return env
    
    def start(self):
        """Запускает все парсеры и координатор"""
        logger.info("Запуск мульти-чат координатора...")
        
        # Очищаем старые сообщения
        self.clear_messages()
        
        # Запускаем парсеры для каждого канала
        for channel in self.channels_config:
            self.start_channel_parser(channel)
        
        # Запускаем основной цикл объединения сообщений
        self.start_message_merger()
        
        logger.info("Мульти-чат координатор запущен")
    
    def start_channel_parser(self, channel):
        """Запускает парсер для конкретного канала"""
        channel_id = channel['prefix'].replace('[', '').replace(']', '').lower()
        temp_file = f"temp_messages_{channel_id}.json"
        
        logger.info(f"Запуск парсера для канала {channel['name']} ({channel['prefix']})")
        
        try:
            # Создаём временный файл для этого канала
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            
            # Запускаем парсер через venv Python
            venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "python.exe")
            
            process = subprocess.Popen(
                [venv_python, "chat_parser_pytchat.py", channel['url'], "--output", temp_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                env=self.get_clean_env()
            )
            
            self.parser_processes[channel_id] = {
                'process': process,
                'channel': channel,
                'temp_file': temp_file
            }
            
            # Создаём очередь для сообщений этого канала
            self.message_queues[channel_id] = Queue()
            
            # Запускаем поток для чтения сообщений из временного файла
            reader_thread = threading.Thread(
                target=self.read_channel_messages,
                args=(channel_id, temp_file, channel),
                daemon=True
            )
            reader_thread.start()
            self.reader_threads[channel_id] = reader_thread
            
            logger.info(f"Парсер для канала {channel['name']} запущен (PID: {process.pid})")
            
        except Exception as e:
            logger.error(f"Ошибка запуска парсера для канала {channel['name']}: {e}")
    
    def read_channel_messages(self, channel_id, temp_file, channel):
        """Читает сообщения из временного файла канала"""
        last_message_count = 0
        consecutive_errors = 0
        last_activity_time = time.time()
        
        INACTIVITY_TIMEOUT = 600  # 10 минут без активности считаем нормой для тихих чатов

        while not self.stop_flag.is_set():
            try:
                # Проверяем, существует ли файл
                if not os.path.exists(temp_file):
                    time.sleep(1)
                    continue
                
                # Читаем сообщения из временного файла
                with open(temp_file, 'r', encoding='utf-8') as f:
                    try:
                        messages = json.load(f)
                    except json.JSONDecodeError:
                        # Файл может быть в процессе записи
                        consecutive_errors += 1
                        if consecutive_errors > 10:
                            logger.warning(f"⚠️ Канал {channel['name']}: много ошибок чтения JSON, возможно парсер завис")
                        time.sleep(0.5)
                        continue
                
                # Сбрасываем счетчик ошибок при успешном чтении
                consecutive_errors = 0
                
                # Если появились новые сообщения
                if len(messages) > last_message_count:
                    new_messages = messages[last_message_count:]
                    
                    # Проверяем на слишком высокую активность
                    if len(new_messages) > 200:
                        logger.warning(f"🔥 Канал {channel['name']}: высокая активность - {len(new_messages)} сообщений за цикл")
                    
                    for message in new_messages:
                        # Добавляем информацию об источнике и префикс
                        enhanced_message = self.enhance_message(message, channel)
                        
                        # Добавляем в очередь с проверкой размера
                        queue_size = self.message_queues[channel_id].qsize()
                        if queue_size > 500:  # Если очередь переполнена
                            logger.warning(f"⚠️ Канал {channel['name']}: переполнение очереди ({queue_size} сообщений)")
                            # Очищаем часть очереди
                            try:
                                for _ in range(50):
                                    self.message_queues[channel_id].get_nowait()
                            except Exception:
                                pass
                        
                        self.message_queues[channel_id].put(enhanced_message)
                    
                    last_message_count = len(messages)
                    last_activity_time = time.time()
                    logger.debug(f"Получено {len(new_messages)} новых сообщений от канала {channel['name']}")
                
                # Проверяем на зависание парсера (нет новых сообщений долгое время)
                elif len(messages) < last_message_count:
                    # Файл был обнулён (например, при рестарте парсера). Синхронизируем счётчик.
                    last_message_count = len(messages)
                    last_activity_time = time.time()
                elif time.time() - last_activity_time > INACTIVITY_TIMEOUT:
                    logger.warning(f"⏰ Канал {channel['name']}: нет активности {INACTIVITY_TIMEOUT // 60} минут, возможно парсер завис")
                    
                    parser_info = self.parser_processes.get(channel_id)
                    process_alive = False
                    if parser_info:
                        process = parser_info.get('process')
                        process_alive = process.poll() is None if process else False
                    
                    # Помечаем канал для перезапуска
                    if not hasattr(self, 'restart_queue'):
                        self.restart_queue = set()
                    
                    if process_alive:
                        self.restart_queue.add(channel_id)
                    else:
                        logger.warning(f"ℹ️ Канал {channel['name']}: процесс парсера уже остановлен, ожидаем автоматический перезапуск")
                    
                    last_activity_time = time.time()  # Сбрасываем чтобы не спамить
                
                time.sleep(1)  # Проверяем каждую секунду
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Ошибка чтения сообщений канала {channel['name']}: {e}")
                
                # Если много ошибок подряд, увеличиваем задержку
                if consecutive_errors > 5:
                    logger.warning(f"⚠️ Канал {channel['name']}: {consecutive_errors} ошибок подряд, увеличиваем задержку")
                    time.sleep(min(consecutive_errors, 30))  # Максимум 30 секунд
                else:
                    time.sleep(5)
    
    def enhance_message(self, message, channel):
        """Добавляет информацию об источнике и префикс к сообщению"""
        import copy
        enhanced = copy.deepcopy(message)  # Глубокая копия для сохранения всех данных
        
        # Добавляем информацию об источнике
        enhanced['source'] = {
            'platform': 'youtube',
            'channel_id': channel['prefix'].replace('[', '').replace(']', '').lower(),
            'channel_name': channel['name'],
            'prefix': channel['prefix']
        }
        
        # Добавляем префикс к отображаемому имени, сохраняя все роли
        if 'author' in enhanced and 'name' in enhanced['author']:
            original_name = enhanced['author']['name']
            enhanced['author']['display_name'] = f"{channel['prefix']} {original_name}"
            
            # Логируем роли для отладки
            roles = []
            if enhanced['author'].get('is_owner'):
                roles.append('owner')
            if enhanced['author'].get('is_moderator'):
                roles.append('moderator')
            if enhanced['author'].get('is_sponsor'):
                roles.append('sponsor')
            
            if roles:
                logger.debug(f"Сообщение от {enhanced['author']['display_name']} (роли: {', '.join(roles)}): {enhanced['text'][:50]}...")
            else:
                logger.debug(f"Сообщение от {enhanced['author']['display_name']}: {enhanced['text'][:50]}...")
        
        return enhanced
    
    def start_message_merger(self):
        """Запускает основной цикл объединения сообщений"""
        merger_thread = threading.Thread(target=self.merge_messages_loop, daemon=True)
        merger_thread.start()
    
    def merge_messages_loop(self):
        """Основной цикл объединения сообщений от всех каналов"""
        logger.info("Запуск цикла объединения сообщений")
        
        while not self.stop_flag.is_set():
            try:
                new_messages = []
                channel_message_counts = {}
                
                # Собираем сообщения из всех очередей
                for channel_id, queue in self.message_queues.items():
                    channel_messages = 0
                    try:
                        # Если оптимизация включена, используем ограничения
                        if self.performance_optimization_enabled and self.max_messages_per_channel_per_cycle:
                            max_messages = self.max_messages_per_channel_per_cycle
                        else:
                            max_messages = float('inf')  # Без ограничений
                        
                        while channel_messages < max_messages:
                            message = queue.get_nowait()
                            new_messages.append(message)
                            channel_messages += 1
                            
                            # Задержка только если оптимизация включена
                            if self.performance_optimization_enabled and self.message_processing_delay > 0:
                                time.sleep(self.message_processing_delay)
                                
                    except Empty:
                        pass
                    
                    if channel_messages > 0:
                        channel_message_counts[channel_id] = channel_messages
                
                # Если есть новые сообщения
                if new_messages:
                    # Фильтруем дубликаты по ID перед добавлением
                    unique_messages = []
                    for msg in new_messages:
                        msg_id = msg.get('id')
                        if msg_id and msg_id not in self.seen_message_ids:
                            unique_messages.append(msg)
                            self.seen_message_ids.add(msg_id)
                        elif not msg_id:
                            # Если нет ID, добавляем сообщение (но это редкий случай)
                            unique_messages.append(msg)
                    
                    # Добавляем только уникальные сообщения к общему списку
                    if unique_messages:
                        self.all_messages.extend(unique_messages)
                        
                        # Сортируем по времени (timestamp)
                        self.all_messages.sort(key=lambda x: x.get('timestamp', 0))
                    
                        # Ограничиваем количество сообщений с умной логикой
                        if len(self.all_messages) > self.max_messages:
                            # Сохраняем пропорционально от каждого канала
                            old_length = len(self.all_messages)
                            self.all_messages = self.smart_trim_messages(self.all_messages)
                            
                            # Обновляем seen_message_ids - удаляем ID сообщений, которые были удалены
                            current_ids = {msg.get('id') for msg in self.all_messages if msg.get('id')}
                            self.seen_message_ids = current_ids
                        
                        # Сохраняем в файл
                        self.save_messages()
                        
                        # Логируем с детализацией по каналам
                        total_new = len(new_messages)
                        unique_new = len(unique_messages)
                        duplicates = total_new - unique_new
                        channel_details = ", ".join([f"{ch_id}: {count}" for ch_id, count in channel_message_counts.items()])
                        
                        if duplicates > 0:
                            logger.info(f"Объединено {unique_new} уникальных ({duplicates} дубликатов) из {total_new} ({channel_details}), всего: {len(self.all_messages)}")
                        else:
                            logger.info(f"Объединено {unique_new} сообщений ({channel_details}), всего: {len(self.all_messages)}")
                    
                    # Предупреждение о высокой нагрузке и автоматическая оптимизация
                    if total_new > 400:
                        logger.warning(f"🔥 Нестандартно большая партия: {total_new} сообщений за цикл")
                
                # Интервал зависит от режима оптимизации
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Ошибка в цикле объединения сообщений: {e}")
                time.sleep(5)
    
    def save_messages(self):
        """Сохраняет объединённые сообщения в файл"""
        with self.write_lock:
            try:
                with open(self.output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.all_messages, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(f"Ошибка сохранения сообщений: {e}")
    
    def clear_messages(self):
        """Очищает файл сообщений"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            self.all_messages = []
            self.seen_message_ids.clear()  # Очищаем множество ID
            logger.info("Файл сообщений очищен")
        except Exception as e:
            logger.error(f"Ошибка очистки сообщений: {e}")
    
    def stop(self):
        """Останавливает все парсеры и координатор"""
        logger.info("Остановка мульти-чат координатора...")
        
        # Устанавливаем флаг остановки
        self.stop_flag.set()
        
        # Останавливаем все процессы парсеров
        for channel_id, parser_info in self.parser_processes.items():
            try:
                process = parser_info['process']
                if process.poll() is None:  # Процесс ещё работает
                    process.terminate()
                    logger.info(f"Парсер канала {parser_info['channel']['name']} остановлен")
                
                # Удаляем временный файл
                temp_file = parser_info['temp_file']
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.debug(f"Временный файл {temp_file} удалён")
                    
            except Exception as e:
                logger.error(f"Ошибка остановки парсера канала {channel_id}: {e}")
        
        # Сохраняем финальное состояние
        if self.all_messages:
            self.save_messages()
        
        logger.info("Мульти-чат координатор остановлен")
    
    def get_status(self):
        """Возвращает статус всех каналов"""
        status = {}
        
        for channel_id, parser_info in self.parser_processes.items():
            process = parser_info['process']
            channel = parser_info['channel']
            
            if process.poll() is None:
                status[channel_id] = {
                    'name': channel['name'],
                    'prefix': channel['prefix'],
                    'status': 'Работает',
                    'pid': process.pid
                }
            else:
                status[channel_id] = {
                    'name': channel['name'],
                    'prefix': channel['prefix'],
                    'status': 'Остановлен',
                    'pid': None
                }
        
        return status
    
    def smart_trim_messages(self, messages):
        """Умное обрезание сообщений с сохранением пропорций от каждого канала"""
        if len(messages) <= self.max_messages:
            return messages
        
        # Группируем сообщения по каналам
        channel_messages = {}
        for msg in messages:
            if 'source' in msg and 'channel_id' in msg['source']:
                channel_id = msg['source']['channel_id']
                if channel_id not in channel_messages:
                    channel_messages[channel_id] = []
                channel_messages[channel_id].append(msg)
            else:
                # Сообщения без источника (обычный чат)
                if 'unknown' not in channel_messages:
                    channel_messages['unknown'] = []
                channel_messages['unknown'].append(msg)
        
        # Если каналов нет, просто берем последние сообщения
        if not channel_messages:
            return messages[-self.max_messages:]
        
        # Вычисляем сколько сообщений оставить от каждого канала
        num_channels = len(channel_messages)
        messages_per_channel = max(self.max_messages // num_channels, 5)  # Минимум 5 на канал
        
        result_messages = []
        
        for channel_id, ch_messages in channel_messages.items():
            # Берем последние сообщения от каждого канала
            channel_limit = min(len(ch_messages), messages_per_channel)
            result_messages.extend(ch_messages[-channel_limit:])
        
        # Сортируем по времени и ограничиваем общий лимит
        result_messages.sort(key=lambda x: x.get('timestamp', 0))
        
        if len(result_messages) > self.max_messages:
            result_messages = result_messages[-self.max_messages:]
        
        logger.debug(f"🔄 Умное обрезание: было {len(messages)}, стало {len(result_messages)} сообщений")
        return result_messages
    
    def restart_channel(self, channel):
        """Перезапускает отдельный канал с кулдауном"""
        channel_id = channel['prefix'].replace('[', '').replace(']', '').lower()
        current_time = time.time()
        
        # Проверяем кулдаун (минимум 60 секунд между перезапусками)
        if channel_id in self.channel_restart_cooldown:
            last_restart = self.channel_restart_cooldown[channel_id]
            if current_time - last_restart < 60:
                logger.info(f"⏳ Канал {channel['name']} в кулдауне, пропускаем перезапуск")
                return
        
        logger.warning(f"🔄 Перезапуск канала {channel['name']} ({channel['prefix']})")
        
        # Останавливаем старый процесс если он есть
        if channel_id in self.parser_processes:
            try:
                old_process = self.parser_processes[channel_id]['process']
                if old_process.poll() is None:
                    logger.info(f"🛑 Останавливаем старый процесс канала {channel['name']} (PID: {old_process.pid})")
                    old_process.terminate()
                    
                    # Ждем завершения процесса
                    try:
                        old_process.wait(timeout=5)  # Ждем 5 секунд
                        logger.info(f"✅ Процесс канала {channel['name']} завершен корректно")
                    except subprocess.TimeoutExpired:
                        logger.warning(f"⚠️ Процесс канала {channel['name']} не отвечает, принудительное завершение")
                        old_process.kill()
                        old_process.wait()
                        logger.info(f"💀 Процесс канала {channel['name']} принудительно завершен")
                
                # Удаляем временный файл
                old_temp_file = self.parser_processes[channel_id]['temp_file']
                if os.path.exists(old_temp_file):
                    os.remove(old_temp_file)
                    logger.debug(f"🗑️ Временный файл {old_temp_file} удалён")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка остановки старого процесса канала {channel['name']}: {e}")
        
        # Запускаем новый процесс
        try:
            self.start_channel_parser(channel)
            self.channel_restart_cooldown[channel_id] = current_time
            logger.info(f"✅ Канал {channel['name']} перезапущен успешно")
        except Exception as e:
            logger.error(f"❌ Ошибка перезапуска канала {channel['name']}: {e}")

# =============================================================================
# ФУНКЦИИ УПРАВЛЕНИЯ
# =============================================================================

def load_settings():
    """Загружает настройки из файла"""
    try:
        with open('chat_settings.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Не удалось загрузить chat_settings.json: {e}")
        return {}

def write_status(status):
    """Записывает статус в файл для GUI"""
    try:
        with open('multichat_status.txt', 'w', encoding='utf-8') as f:
            f.write(status)
    except Exception:
        pass

def main():
    parser = argparse.ArgumentParser(description='YouTube Multi-Chat Coordinator')
    parser.add_argument('--output', '-o', default='messages.json', help='Файл для сохранения объединённых сообщений')
    parser.add_argument('--max-messages', '-m', type=int, default=50, help='Максимальное количество сообщений')
    
    args = parser.parse_args()
    
    # Загружаем настройки
    settings = load_settings()
    
    # Проверяем, включён ли мульти-чат
    if not settings.get('multichat_enabled', False):
        logger.error("Мульти-чат не включён в настройках")
        write_status("ERROR: Multichat disabled")
        return
    
    # Получаем список каналов
    channels = settings.get('multichat_channels', [])
    if not channels:
        logger.error("Не найдено каналов для мульти-чата")
        write_status("ERROR: No channels")
        return
    
    # Фильтруем только активные каналы с корректными URL
    active_channels = []
    for channel in channels:
        if channel.get('url') and channel.get('name') and channel.get('prefix'):
            active_channels.append(channel)
        else:
            logger.warning(f"Пропущен некорректный канал: {channel}")
    
    if not active_channels:
        logger.error("Не найдено корректных каналов")
        write_status("ERROR: No valid channels")
        return
    
    logger.info(f"Найдено {len(active_channels)} активных каналов")
    
    # Создаём и запускаем координатор с настройками производительности
    # Для мульти-чата используем увеличенный лимит сообщений
    multichat_max_messages = max(args.max_messages * len(active_channels), 100)  # Минимум 100, или по количеству каналов
    
    coordinator = MultiChatCoordinator(
        channels_config=active_channels,
        output_file=args.output,
        max_messages=multichat_max_messages
    )
    
    logger.info(f"📊 Лимит сообщений для мульти-чата: {multichat_max_messages} (каналов: {len(active_channels)})")
    
    # Применяем настройки производительности из файла (только если включены)
    coordinator.performance_optimization_enabled = settings.get('performance_optimization_enabled', False)
    coordinator.auto_protection_enabled = settings.get('auto_performance_protection', True)
    
    if coordinator.performance_optimization_enabled:
        coordinator.max_messages_per_channel_per_cycle = settings.get('max_messages_per_channel_per_cycle', 10)
        coordinator.message_processing_delay = settings.get('message_processing_delay', 0.1)
        logger.info(f"⚡ Оптимизация производительности ВКЛЮЧЕНА: макс. сообщений на канал = {coordinator.max_messages_per_channel_per_cycle}, задержка = {coordinator.message_processing_delay}с")
    else:
        logger.info("🚀 Режим максимальной производительности (без ограничений)")
    
    try:
        write_status("STARTING")
        coordinator.start()
        write_status("RUNNING")
        
        # Основной цикл с мониторингом и перезапуском отдельных каналов
        while True:
            time.sleep(10)
            
            # Проверяем статус каналов
            status = coordinator.get_status()
            running_count = sum(1 for s in status.values() if s['status'] == 'Работает')
            
            write_status(f"RUNNING: {running_count}/{len(active_channels)} channels")
            
            # Логируем подробный статус каналов с дополнительной диагностикой
            for channel_id, channel_status in status.items():
                if channel_status['status'] == 'Работает':
                    # Проверяем размер очереди для диагностики
                    queue_size = coordinator.message_queues.get(channel_id, Queue()).qsize()
                    if queue_size > 50:
                        logger.warning(f"⚠️ Канал {channel_status['name']}: большая очередь ({queue_size} сообщений)")
                    else:
                        logger.debug(f"✅ Канал {channel_status['name']} работает (PID: {channel_status['pid']}, очередь: {queue_size})")
                else:
                    logger.warning(f"❌ Канал {channel_status['name']} остановлен")
            
            # Перезапускаем каналы из очереди (зависшие)
            if hasattr(coordinator, 'restart_queue') and coordinator.restart_queue:
                channels_to_restart = coordinator.restart_queue.copy()
                coordinator.restart_queue.clear()
                
                for channel_id in channels_to_restart:
                    logger.warning(f"🔄 Перезапуск зависшего канала: {channel_id}")
                    
                    # Находим конфигурацию канала
                    channel_config = None
                    for channel in active_channels:
                        if channel['prefix'].replace('[', '').replace(']', '').lower() == channel_id:
                            channel_config = channel
                            break
                    
                    if channel_config:
                        coordinator.restart_channel(channel_config)
                    else:
                        logger.error(f"❌ Не найдена конфигурация для зависшего канала {channel_id}")
            
            # Перезапускаем отдельные отключившиеся каналы
            for channel_id, channel_status in status.items():
                if channel_status['status'] == 'Остановлен':
                    logger.warning(f"🔄 Канал {channel_status['name']} отключился, перезапускаем...")
                    
                    # Находим конфигурацию канала
                    channel_config = None
                    for channel in active_channels:
                        if channel['prefix'].replace('[', '').replace(']', '').lower() == channel_id:
                            channel_config = channel
                            break
                    
                    if channel_config:
                        coordinator.restart_channel(channel_config)
                    else:
                        logger.error(f"❌ Не найдена конфигурация для канала {channel_id}")
            
            # Если все парсеры остановились, полный перезапуск
            if running_count == 0:
                logger.warning("Все парсеры остановились, полный перезапуск...")
                coordinator.stop()
                time.sleep(5)
                coordinator = MultiChatCoordinator(
                    channels_config=active_channels,
                    output_file=args.output,
                    max_messages=args.max_messages
                )
                coordinator.start()
    
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
        write_status("STOPPING")
        coordinator.stop()
        write_status("STOPPED")
    
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)
        write_status(f"ERROR: {str(e)}")
        coordinator.stop()

if __name__ == "__main__":
    main()
