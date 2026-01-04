#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Монитор мульти-чата для отслеживания зависших каналов
"""

import os
import json
import time
import subprocess
from datetime import datetime

def check_multichat_status():
    """Проверяет статус мульти-чата и каналов"""
    print(f"🔍 Мониторинг мульти-чата - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    # Проверяем статус файл
    try:
        with open('multichat_status.txt', 'r', encoding='utf-8') as f:
            status = f.read().strip()
            print(f"📊 Общий статус: {status}")
    except FileNotFoundError:
        print("❌ Файл статуса не найден - мульти-чат не запущен")
        return
    
    # Проверяем временные файлы каналов
    temp_files = []
    for file in os.listdir('.'):
        if file.startswith('temp_messages_') and file.endswith('.json'):
            temp_files.append(file)
    
    if not temp_files:
        print("📁 Временные файлы каналов не найдены")
        return
    
    print(f"\n📁 Найдено каналов: {len(temp_files)}")
    
    for temp_file in temp_files:
        channel_id = temp_file.replace('temp_messages_', '').replace('.json', '')
        
        try:
            # Проверяем размер файла
            file_size = os.path.getsize(temp_file)
            
            # Проверяем время последнего изменения
            mtime = os.path.getmtime(temp_file)
            last_modified = datetime.fromtimestamp(mtime)
            time_diff = (datetime.now() - last_modified).total_seconds()
            
            # Проверяем количество сообщений
            try:
                with open(temp_file, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
                    message_count = len(messages)
            except:
                message_count = "Ошибка чтения"
            
            # Определяем статус канала
            if time_diff > 300:  # 5 минут без изменений
                status_icon = "💀"
                status_text = "ЗАВИС"
            elif time_diff > 120:  # 2 минуты без изменений
                status_icon = "⚠️"
                status_text = "ПОДОЗРЕНИЕ"
            else:
                status_icon = "✅"
                status_text = "АКТИВЕН"
            
            print(f"{status_icon} Канал {channel_id.upper()}:")
            print(f"   Сообщений: {message_count}")
            print(f"   Размер файла: {file_size} байт")
            print(f"   Последнее обновление: {int(time_diff)}с назад")
            print(f"   Статус: {status_text}")
            print()
            
        except Exception as e:
            print(f"❌ Ошибка проверки канала {channel_id}: {e}")
    
    # Проверяем процессы Python
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            python_processes = [line for line in lines if 'python.exe' in line.lower()]
            
            print(f"🐍 Python процессов: {len(python_processes)}")
            for proc in python_processes[:5]:  # Показываем первые 5
                if proc.strip():
                    parts = proc.split()
                    if len(parts) >= 2:
                        print(f"   PID: {parts[1]}")
    except:
        print("❌ Не удалось получить список процессов")

def main():
    """Основная функция мониторинга"""
    try:
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')  # Очищаем экран
            check_multichat_status()
            
            print("🔄 Обновление через 30 секунд... (Ctrl+C для выхода)")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n👋 Мониторинг остановлен")

if __name__ == "__main__":
    main()
