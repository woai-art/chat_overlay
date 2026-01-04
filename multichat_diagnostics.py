#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Диагностика мульти-чата
Проверяет состояние всех компонентов мульти-чат системы
"""

import os
import json
import subprocess
import time
from datetime import datetime

def check_file_exists(filepath, description):
    """Проверяет существование файла"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        print(f"✅ {description}: {filepath} (размер: {size} байт, изменён: {mtime})")
        return True
    else:
        print(f"❌ {description}: {filepath} - НЕ НАЙДЕН")
        return False

def check_multichat_settings():
    """Проверяет настройки мульти-чата"""
    print("\n🔧 ПРОВЕРКА НАСТРОЕК МУЛЬТИ-ЧАТА:")
    
    if not check_file_exists('chat_settings.json', 'Файл настроек'):
        return False
    
    try:
        with open('chat_settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        multichat_enabled = settings.get('multichat_enabled', False)
        channels = settings.get('multichat_channels', [])
        
        print(f"📊 Мульти-чат включён: {multichat_enabled}")
        print(f"📊 Количество каналов: {len(channels)}")
        
        if multichat_enabled and channels:
            print("📋 Каналы:")
            for i, channel in enumerate(channels, 1):
                prefix = channel.get('prefix', 'N/A')
                name = channel.get('name', 'N/A')
                url = channel.get('url', 'N/A')
                print(f"   {i}. {prefix} {name}")
                print(f"      URL: {url[:60]}...")
        
        return multichat_enabled and len(channels) > 0
        
    except Exception as e:
        print(f"❌ Ошибка чтения настроек: {e}")
        return False

def check_processes():
    """Проверяет запущенные процессы"""
    print("\n🔍 ПРОВЕРКА ПРОЦЕССОВ:")
    
    try:
        # Проверяем процессы Python
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            python_processes = [line for line in lines if 'python.exe' in line.lower()]
            
            print(f"🐍 Найдено Python процессов: {len(python_processes)}")
            for proc in python_processes:
                if proc.strip():
                    parts = proc.split()
                    if len(parts) >= 2:
                        print(f"   PID: {parts[1]}")
        else:
            print("❌ Не удалось получить список процессов")
            
    except Exception as e:
        print(f"❌ Ошибка проверки процессов: {e}")

def check_temp_files():
    """Проверяет временные файлы каналов"""
    print("\n📁 ПРОВЕРКА ВРЕМЕННЫХ ФАЙЛОВ:")
    
    temp_files = []
    for file in os.listdir('.'):
        if file.startswith('temp_messages_') and file.endswith('.json'):
            temp_files.append(file)
    
    if temp_files:
        print(f"📊 Найдено временных файлов: {len(temp_files)}")
        for temp_file in temp_files:
            check_file_exists(temp_file, f'Временный файл канала')
    else:
        print("📊 Временные файлы каналов не найдены")

def check_logs():
    """Проверяет лог файлы"""
    print("\n📋 ПРОВЕРКА ЛОГОВ:")
    
    log_files = [
        ('multichat.log', 'Лог мульти-чата'),
        ('parser.log', 'Лог парсера'),
        ('gui.log', 'Лог GUI'),
        ('parser_status.txt', 'Статус парсера'),
        ('multichat_status.txt', 'Статус мульти-чата')
    ]
    
    for log_file, description in log_files:
        if check_file_exists(log_file, description):
            # Показываем последние строки лога
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        last_lines = lines[-3:] if len(lines) >= 3 else lines
                        print(f"   Последние записи:")
                        for line in last_lines:
                            print(f"   > {line.strip()}")
            except Exception as e:
                print(f"   ❌ Ошибка чтения: {e}")

def check_main_files():
    """Проверяет основные файлы системы"""
    print("\n📄 ПРОВЕРКА ОСНОВНЫХ ФАЙЛОВ:")
    
    main_files = [
        ('messages.json', 'Основной файл сообщений'),
        ('multichat_coordinator.py', 'Координатор мульти-чата'),
        ('chat_parser_pytchat.py', 'Парсер чата'),
        ('chat_gui_simple.py', 'GUI приложения'),
        ('vmix_simple.html', 'HTML интерфейс')
    ]
    
    all_exist = True
    for filepath, description in main_files:
        if not check_file_exists(filepath, description):
            all_exist = False
    
    return all_exist

def main():
    """Основная функция диагностики"""
    print("🔍 ДИАГНОСТИКА МУЛЬТИ-ЧАТА YouTube Live Chat")
    print("=" * 60)
    
    # Проверяем основные файлы
    files_ok = check_main_files()
    
    # Проверяем настройки
    settings_ok = check_multichat_settings()
    
    # Проверяем процессы
    check_processes()
    
    # Проверяем временные файлы
    check_temp_files()
    
    # Проверяем логи
    check_logs()
    
    # Итоговый статус
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ СТАТУС:")
    
    if files_ok and settings_ok:
        print("✅ Система готова к работе")
        print("💡 Рекомендации:")
        print("   • Запустите GUI и включите мульти-чат")
        print("   • Добавьте каналы через интерфейс")
        print("   • Используйте кнопку '📋 Показать логи' для мониторинга")
    else:
        print("❌ Обнаружены проблемы")
        if not files_ok:
            print("   • Проверьте наличие всех файлов системы")
        if not settings_ok:
            print("   • Настройте мульти-чат в GUI")
    
    print("\n🔧 Для решения проблем:")
    print("   1. Откройте GUI (chat_gui_simple.py)")
    print("   2. Перейдите на вкладку 'Мульти-чат'")
    print("   3. Включите мульти-чат и добавьте каналы")
    print("   4. Используйте '📋 Показать логи' для диагностики")

if __name__ == "__main__":
    main()
