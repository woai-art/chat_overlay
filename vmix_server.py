#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import http.server
import socketserver
import os
import sys
import webbrowser
from urllib.parse import urlparse

class vMixHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP сервер оптимизированный для vMix"""
    
    def end_headers(self):
        # Добавляем заголовки для совместимости с vMix
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Обрабатываем OPTIONS запросы для CORS"""
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Логирование запросов"""
        message = format % args
        print(f"[{self.log_date_time_string()}] {message}")
        
        # Специальное логирование для vMix
        if "chat_local.html" in message:
            print("✅ vMix запросил основной чат")
        elif "vmix_debug.html" in message:
            print("🔧 vMix запросил отладочную версию")
        elif "messages.json" in message:
            print("📨 vMix запросил сообщения")

def main():
    PORT = 8080
    
    # Проверяем наличие необходимых файлов
    required_files = ['chat_local.html', 'chat_local.js', 'style.css']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Отсутствуют необходимые файлы:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nПроверьте, что вы запускаете сервер из папки chat_overlay")
        input("Нажмите Enter для выхода...")
        return
    
    # Меняем рабочую директорию на папку скрипта
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        with socketserver.TCPServer(("", PORT), vMixHTTPRequestHandler) as httpd:
            print(f"🚀 vMix HTTP Сервер запущен на порту {PORT}")
            print(f"📁 Рабочая папка: {os.getcwd()}")
            print()
            print("🌐 Доступные URL для vMix:")
            print(f"   Основной чат:     http://localhost:{PORT}/chat_local.html")
            print(f"   Отладка vMix:     http://localhost:{PORT}/vmix_debug.html")
            print(f"   Демо тем:         http://localhost:{PORT}/theme_demo.html")
            print()
            print("💡 Для vMix используйте: http://localhost:8080/chat_local.html")
            print("🛑 Для остановки нажмите Ctrl+C")
            print("=" * 60)
            
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 10048:  # Address already in use
            print(f"❌ Порт {PORT} уже используется!")
            print("💡 Возможные решения:")
            print("   1. Закройте другой HTTP сервер")
            print("   2. Перезагрузите компьютер")
            print("   3. Измените порт в настройках")
        else:
            print(f"❌ Ошибка запуска сервера: {e}")
        
        input("Нажмите Enter для выхода...")
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")

if __name__ == "__main__":
    main() 