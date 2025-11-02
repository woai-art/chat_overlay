import http.server
import socketserver
import os
import sys
import json

# Определяем порт из аргументов командной строки или используем 8080 по умолчанию
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

# Определяем директорию, в которой находится скрипт
web_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(web_dir)

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    # Переопределяем метод для добавления правильных MIME-типов
    def guess_type(self, path):
        if path.endswith('.js'):
            return 'application/javascript'
        if path.endswith('.json'):
            return 'application/json'
        if path.endswith('.css'):
            return 'text/css'
        if path.endswith('.html'):
            return 'text/html'
        return super().guess_type(path)

    # Логирование запросов для отладки
    def log_message(self, format, *args):
        print(f"[ВЕБ-СЕРВЕР] {self.address_string()} - {args[0]} {args[1]}")

# Создаем сервер с возможностью переиспользования адреса
# Это помогает избежать ошибки "Address already in use" при быстром перезапуске
socketserver.TCPServer.allow_reuse_address = True
Handler = MyHttpRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)

print("==========================================")
print(f"  УЛУЧШЕННЫЙ ВЕБ-СЕРВЕР ЗАПУЩЕН")
print("==========================================")
print(f"  Порт: {PORT}")
print(f"  Рабочая папка: {web_dir}")
print("==========================================")
print("  Доступные ссылки:")
print(f"  - Основной чат: http://localhost:{PORT}/chat_local.html")
print(f"  - Демо тем:     http://localhost:{PORT}/theme_demo.html")
print("==========================================")
print("  Для остановки сервера нажмите Ctrl+C")
print("==========================================")

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\n[ВЕБ-СЕРВЕР] Остановка сервера...")
    httpd.server_close()
    sys.exit(0)