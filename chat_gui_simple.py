#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess
import threading
import webbrowser
import time

class YouTubeChatGUISimple:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Live Chat Overlay - Управление")
        self.root.geometry("700x600")
        
        # Переменные для процессов
        self.parser_process = None
        self.server_process = None
        
        # Настройки по умолчанию
        self.settings = {
            'chat_width': '84vw',
            'chat_height': '92vh',
            'chat_position_x': '2vw',
            'chat_position_y': '8vh',
            'font_size': '2.8em',
            'message_lifetime': 900,
            'max_messages': 50,
            'show_avatars': True,
            'fade_effect': True,
            'highlight_sponsors': True,
            'show_user_badges': True,
            'server_port': 8080,
            'video_url': '',
            'update_interval': 1,
            'theme': 'barbie'
        }
        
        self.load_settings()
        self.create_gui()
        
    def create_gui(self):
        # Главный фрейм с вкладками
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка 1: Трансляция
        stream_frame = ttk.Frame(notebook)
        notebook.add(stream_frame, text="Трансляция")
        self.create_stream_tab(stream_frame)
        
        # Вкладка 2: Настройки отображения
        display_frame = ttk.Frame(notebook)
        notebook.add(display_frame, text="Настройки отображения")
        self.create_display_tab(display_frame)
        
        # Вкладка 3: Управление
        control_frame = ttk.Frame(notebook)
        notebook.add(control_frame, text="Управление")
        self.create_control_tab(control_frame)
        
    def create_stream_tab(self, parent):
        # Секция ввода URL
        url_group = ttk.LabelFrame(parent, text="YouTube трансляция", padding=10)
        url_group.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(url_group, text="URL YouTube трансляции:").pack(anchor='w')
        ttk.Label(url_group, text="(например: https://www.youtube.com/watch?v=VIDEO_ID)", 
                 foreground="gray").pack(anchor='w', pady=(0,5))
        
        self.url_var = tk.StringVar(value=self.settings.get('video_url', ''))
        self.url_entry = ttk.Entry(url_group, textvariable=self.url_var, width=80)
        self.url_entry.pack(fill='x', pady=5)
        
        # Добавляем поддержку стандартных горячих клавиш
        self.url_entry.bind('<Control-v>', self.paste_url)
        self.url_entry.bind('<Control-a>', self.select_all_url)
        self.url_entry.bind('<Control-c>', self.copy_url)
        self.url_entry.bind('<Control-x>', self.cut_url)
        
        button_frame = ttk.Frame(url_group)
        button_frame.pack(fill='x', pady=5)
        
        ttk.Button(button_frame, text="Проверить URL", command=self.validate_url).pack(side='left')
        ttk.Button(button_frame, text="📋 Вставить", command=self.paste_from_clipboard).pack(side='left', padx=(5,0))
        ttk.Button(button_frame, text="🧹 Очистить", command=self.clear_url).pack(side='left', padx=(5,0))
        ttk.Button(button_frame, text="Сохранить", command=self.save_url).pack(side='right')
        
        self.url_status_label = ttk.Label(url_group, text="", foreground="gray")
        self.url_status_label.pack(pady=5)
        
        # Примеры и инструкции
        help_group = ttk.LabelFrame(parent, text="Как найти URL трансляции", padding=10)
        help_group.pack(fill='both', expand=True, padx=10, pady=5)
        
        instructions = """Чтобы получить URL YouTube трансляции:

1. Откройте YouTube в браузере
2. Найдите нужную LIVE трансляцию
3. Скопируйте URL из адресной строки браузера
4. Вставьте URL в поле выше (Ctrl+V или кнопка "📋 Вставить")

Примеры корректных URL:
• https://www.youtube.com/watch?v=dQw4w9WgXcQ
• https://youtu.be/dQw4w9WgXcQ
• https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=0s

ВАЖНО: Трансляция должна быть АКТИВНОЙ (LIVE), 
иначе чат работать не будет!

💡 Горячие клавиши:
• Ctrl+V - Вставить из буфера
• Ctrl+A - Выделить всё
• Ctrl+C - Копировать
• Ctrl+X - Вырезать"""
        
        instructions_label = tk.Text(help_group, height=15, wrap='word', 
                                   font=('Segoe UI', 9), state='disabled',
                                   bg=self.root.cget('bg'), relief='flat')
        instructions_label.config(state='normal')
        instructions_label.insert('1.0', instructions)
        instructions_label.config(state='disabled')
        instructions_label.pack(fill='both', expand=True)
        
    def create_display_tab(self, parent):
        # Размеры и позиция
        size_group = ttk.LabelFrame(parent, text="Размер и позиция", padding=10)
        size_group.pack(fill='x', padx=10, pady=5)
        
        # Ширина
        ttk.Label(size_group, text="Ширина чата:").grid(row=0, column=0, sticky='w', pady=2)
        self.width_var = tk.StringVar(value=self.settings['chat_width'])
        ttk.Entry(size_group, textvariable=self.width_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(size_group, text="(например: 84vw, 800px)").grid(row=0, column=2, sticky='w', pady=2)
        
        # Высота
        ttk.Label(size_group, text="Высота чата:").grid(row=1, column=0, sticky='w', pady=2)
        self.height_var = tk.StringVar(value=self.settings['chat_height'])
        ttk.Entry(size_group, textvariable=self.height_var, width=15).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(size_group, text="(например: 25vh, 300px)").grid(row=1, column=2, sticky='w', pady=2)
        
        # Позиция X
        ttk.Label(size_group, text="Позиция X:").grid(row=2, column=0, sticky='w', pady=2)
        self.pos_x_var = tk.StringVar(value=self.settings['chat_position_x'])
        ttk.Entry(size_group, textvariable=self.pos_x_var, width=15).grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(size_group, text="(отступ слева)").grid(row=2, column=2, sticky='w', pady=2)
        
        # Позиция Y
        ttk.Label(size_group, text="Позиция Y:").grid(row=3, column=0, sticky='w', pady=2)
        self.pos_y_var = tk.StringVar(value=self.settings['chat_position_y'])
        ttk.Entry(size_group, textvariable=self.pos_y_var, width=15).grid(row=3, column=1, padx=5, pady=2)
        ttk.Label(size_group, text="(отступ снизу)").grid(row=3, column=2, sticky='w', pady=2)
        
        # Стиль и поведение
        style_group = ttk.LabelFrame(parent, text="Стиль и поведение", padding=10)
        style_group.pack(fill='x', padx=10, pady=5)
        
        # Размер шрифта
        ttk.Label(style_group, text="Размер шрифта:").grid(row=0, column=0, sticky='w', pady=2)
        self.font_size_var = tk.StringVar(value=self.settings['font_size'])
        ttk.Entry(style_group, textvariable=self.font_size_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(style_group, text="(например: 2.8em, 20px)").grid(row=0, column=2, sticky='w', pady=2)
        
        # Время жизни сообщений
        ttk.Label(style_group, text="Время показа (сек):").grid(row=1, column=0, sticky='w', pady=2)
        self.lifetime_var = tk.IntVar(value=self.settings['message_lifetime'])
        ttk.Spinbox(style_group, from_=5, to=1800, textvariable=self.lifetime_var, width=13).grid(row=1, column=1, padx=5, pady=2)
        
        # Максимум сообщений
        ttk.Label(style_group, text="Макс. сообщений:").grid(row=2, column=0, sticky='w', pady=2)
        self.max_msg_var = tk.IntVar(value=self.settings['max_messages'])
        ttk.Spinbox(style_group, from_=5, to=100, textvariable=self.max_msg_var, width=13).grid(row=2, column=1, padx=5, pady=2)
        
        # Чекбоксы
        options_group = ttk.LabelFrame(parent, text="Опции отображения", padding=10)
        options_group.pack(fill='x', padx=10, pady=5)
        
        self.show_avatars_var = tk.BooleanVar(value=self.settings['show_avatars'])
        ttk.Checkbutton(options_group, text="Показывать аватары пользователей", variable=self.show_avatars_var).pack(anchor='w')
        
        self.fade_effect_var = tk.BooleanVar(value=self.settings['fade_effect'])
        ttk.Checkbutton(options_group, text="Эффект затухания сообщений", variable=self.fade_effect_var).pack(anchor='w')
        
        self.highlight_sponsors_var = tk.BooleanVar(value=self.settings['highlight_sponsors'])
        ttk.Checkbutton(options_group, text="Выделять спонсоров канала цветом", variable=self.highlight_sponsors_var).pack(anchor='w')
        
        self.show_badges_var = tk.BooleanVar(value=self.settings['show_user_badges'])
        ttk.Checkbutton(options_group, text="Показывать значки пользователей", variable=self.show_badges_var).pack(anchor='w')
        
        # Выбор темы
        theme_frame = ttk.Frame(options_group)
        theme_frame.pack(fill='x', pady=5)
        
        ttk.Label(theme_frame, text="Тема чата:").pack(side='left')
        self.theme_var = tk.StringVar(value=self.settings.get('theme', 'barbie'))
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, width=20, state='readonly')
        theme_combo['values'] = ('barbie', 'cyberpunk', 'minimal', 'dark-elegant', 'retrowave')
        theme_combo.pack(side='left', padx=(10, 0))
        
        # Кнопка демонстрации тем
        ttk.Button(theme_frame, text="🎨 Демо тем", command=self.open_theme_demo).pack(side='right')
        
        # Сервер
        server_group = ttk.LabelFrame(parent, text="Настройки сервера", padding=10)
        server_group.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(server_group, text="Порт HTTP сервера:").grid(row=0, column=0, sticky='w', pady=2)
        self.port_var = tk.IntVar(value=self.settings['server_port'])
        ttk.Spinbox(server_group, from_=8000, to=9999, textvariable=self.port_var, width=13).grid(row=0, column=1, padx=5, pady=2)
        
        # Кнопки
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Применить настройки", command=self.apply_settings).pack(side='left')
        ttk.Button(button_frame, text="Сброс к умолчанию", command=self.reset_settings).pack(side='right')
        
    def create_control_tab(self, parent):
        # Статус
        status_group = ttk.LabelFrame(parent, text="Статус системы", padding=10)
        status_group.pack(fill='x', padx=10, pady=5)
        
        self.parser_status_label = ttk.Label(status_group, text="Парсер чата: Остановлен", foreground="red")
        self.parser_status_label.pack(anchor='w', pady=2)
        
        self.server_status_label = ttk.Label(status_group, text="HTTP сервер: Остановлен", foreground="red")
        self.server_status_label.pack(anchor='w', pady=2)
        
        # Управление
        control_group = ttk.LabelFrame(parent, text="Управление системой", padding=10)
        control_group.pack(fill='x', padx=10, pady=5)
        
        button_frame1 = ttk.Frame(control_group)
        button_frame1.pack(fill='x', pady=5)
        
        ttk.Button(button_frame1, text="🚀 Запустить всё", command=self.start_all).pack(side='left', padx=(0,5))
        ttk.Button(button_frame1, text="🛑 Остановить всё", command=self.stop_all).pack(side='left', padx=5)
        
        button_frame2 = ttk.Frame(control_group)
        button_frame2.pack(fill='x', pady=5)
        
        ttk.Button(button_frame2, text="Запустить только парсер", command=self.start_parser).pack(side='left', padx=(0,5))
        ttk.Button(button_frame2, text="Запустить только сервер", command=self.start_server).pack(side='left', padx=5)
        
        button_frame3 = ttk.Frame(control_group)
        button_frame3.pack(fill='x', pady=5)
        
        ttk.Button(button_frame3, text="🧹 Очистить чат", command=self.clear_chat).pack(side='left', padx=(0,5))
        ttk.Button(button_frame3, text="🔄 Перезапустить парсер", command=self.restart_parser).pack(side='left', padx=5)
        ttk.Button(button_frame3, text="🧪 Тест парсера", command=self.test_parser).pack(side='left', padx=5)
        
        # Ссылки
        links_group = ttk.LabelFrame(parent, text="Полезные ссылки", padding=10)
        links_group.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(links_group, text="🌐 Открыть чат в браузере", command=self.open_chat_browser).pack(anchor='w', pady=2)
        ttk.Button(links_group, text="📁 Открыть папку проекта", command=self.open_project_folder).pack(anchor='w', pady=2)
        
        # Логи
        logs_group = ttk.LabelFrame(parent, text="Логи", padding=10)
        logs_group.pack(fill='both', expand=True, padx=10, pady=5)
        
        log_frame = ttk.Frame(logs_group)
        log_frame.pack(fill='both', expand=True)
        
        self.log_text = tk.Text(log_frame, height=8, wrap='word')
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')
        
        ttk.Button(logs_group, text="Очистить логи", command=self.clear_logs).pack()
        
    def validate_url(self):
        url = self.url_var.get().strip()
        if not url:
            self.url_status_label.config(text="❌ Введите URL", foreground="red")
            return
            
        # Простая проверка формата YouTube URL
        valid_patterns = [
            'youtube.com/watch?v=',
            'youtu.be/',
            'youtube.com/live/'
        ]
        
        if any(pattern in url for pattern in valid_patterns):
            self.url_status_label.config(text="✅ URL выглядит корректно", foreground="green")
            self.log(f"✅ URL проверен: {url}")
        else:
            self.url_status_label.config(text="⚠️ Возможно неверный формат URL", foreground="orange")
            self.log(f"⚠️ Подозрительный URL: {url}")
            
    def save_url(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Предупреждение", "Введите URL трансляции")
            return
            
        self.settings['video_url'] = url
        self.save_settings()
        self.log(f"💾 URL сохранен: {url}")
        
    def start_all(self):
        if not self.settings.get('video_url'):
            messagebox.showwarning("Предупреждение", "Сначала введите URL трансляции")
            return
            
        self.apply_settings()  # Применяем настройки перед запуском
        self.start_server()
        self.start_parser()
        
    def start_parser(self):
        if not self.settings.get('video_url'):
            messagebox.showwarning("Предупреждение", "Сначала введите URL трансляции")
            return
            
        if self.parser_process and self.parser_process.poll() is None:
            self.log("⚠️ Парсер уже запущен")
            return
            
        try:
            self.log("🚀 Запуск парсера чата...")
            
            # Запускаем парсер через venv Python
            venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "python.exe")
            
            self.parser_process = subprocess.Popen(
                [venv_python, "chat_parser_pytchat.py", self.settings['video_url']],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            self.parser_status_label.config(text="Парсер чата: Работает", foreground="green")
            self.log("✅ Парсер чата запущен")
            
            # Мониторим процесс парсера
            threading.Thread(target=self.monitor_parser, daemon=True).start()
            
        except Exception as e:
            self.log(f"❌ Ошибка запуска парсера: {str(e)}")
            
    def start_server(self):
        if self.server_process and self.server_process.poll() is None:
            self.log("⚠️ Сервер уже запущен")
            return
            
        try:
            self.log("🚀 Запуск HTTP сервера...")
            
            # Запускаем надежный встроенный HTTP сервер через venv Python
            venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "python.exe")
            self.server_process = subprocess.Popen(
                [venv_python, "-m", "http.server", str(self.settings['server_port'])],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            self.server_status_label.config(text="HTTP сервер: Работает", foreground="green")
            self.log(f"✅ HTTP сервер запущен на порту {self.settings['server_port']}")
            
            # Мониторим процесс сервера
            threading.Thread(target=self.monitor_server, daemon=True).start()
            
        except Exception as e:
            self.log(f"❌ Ошибка запуска сервера: {str(e)}")
            
    def stop_all(self):
        self.stop_parser()
        self.stop_server()
        
    def stop_parser(self):
        if self.parser_process:
            self.parser_process.terminate()
            self.parser_process = None
            self.parser_status_label.config(text="Парсер чата: Остановлен", foreground="red")
            self.log("🛑 Парсер чата остановлен")
            
    def stop_server(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None
            self.server_status_label.config(text="HTTP сервер: Остановлен", foreground="red")
            self.log("🛑 HTTP сервер остановлен")
            
    def monitor_parser(self):
        """Мониторинг парсера с проверкой статуса"""
        last_status = ""
        
        while self.parser_process and self.parser_process.poll() is None:
            try:
                # Читаем статус из файла (для GUI версии парсера)
                try:
                    with open('parser_status.txt', 'r', encoding='utf-8') as f:
                        status = f.read().strip()
                        if status and status != last_status:
                            if status.startswith("ERROR"):
                                self.root.after(0, lambda s=status: self.log(f"❌ {s}"))
                                self.root.after(0, lambda: self.parser_status_label.config(text="Парсер чата: Ошибка", foreground="red"))
                            elif status == "CONNECTING":
                                self.root.after(0, lambda: self.log("🔄 Подключение к чату..."))
                                self.root.after(0, lambda: self.parser_status_label.config(text="Парсер чата: Подключение", foreground="orange"))
                            elif status == "CONNECTED":
                                self.root.after(0, lambda: self.log("✅ Подключен к чату"))
                                self.root.after(0, lambda: self.parser_status_label.config(text="Парсер чата: Работает", foreground="green"))
                            elif status.startswith("RUNNING"):
                                # Обновляем счетчик сообщений
                                self.root.after(0, lambda s=status: self.parser_status_label.config(text=f"Парсер чата: {s.split(': ')[1] if ': ' in s else 'Работает'}", foreground="green"))
                            elif status == "FINISHED":
                                self.root.after(0, lambda: self.log("✅ Парсер завершен"))
                                self.root.after(0, lambda: self.parser_status_label.config(text="Парсер чата: Завершен", foreground="gray"))
                            
                            last_status = status
                except FileNotFoundError:
                    pass
                
                time.sleep(1)  # Проверяем каждую секунду
                
            except Exception as error:
                self.root.after(0, lambda err=error: self.log(f"❌ Ошибка мониторинга: {err}"))
                break
        
        # Процесс завершился
        if self.parser_process:
            return_code = self.parser_process.poll()
            if return_code is not None:
                if return_code != 0:
                    self.root.after(0, lambda: self.log(f"❌ Парсер завершился с ошибкой (код: {return_code})"))
                    self.root.after(0, lambda: self.parser_status_label.config(text="Парсер чата: Ошибка", foreground="red"))
                else:
                    self.root.after(0, lambda: self.log("✅ Парсер завершен"))
                    self.root.after(0, lambda: self.parser_status_label.config(text="Парсер чата: Остановлен", foreground="red"))
                
    def monitor_server(self):
        if self.server_process:
            try:
                # Дожидаемся завершения процесса и читаем весь вывод
                stdout, stderr = self.server_process.communicate()

                # Логируем вывод сервера
                if stdout:
                    for line in stdout.split('\n'):
                        if line.strip():
                            self.root.after(0, lambda l=line: self.log(f"[Server] {l}"))
                if stderr:
                    for line in stderr.split('\n'):
                        if line.strip():
                            self.root.after(0, lambda l=line: self.log(f"❌ [Server ERROR] {l}"))

                # Проверяем код возврата
                if self.server_process and self.server_process.returncode != 0:
                    self.root.after(0, lambda: self.log(f"❌ HTTP сервер завершился с ошибкой (код: {self.server_process.returncode})"))
                    self.root.after(0, lambda: self.server_status_label.config(text="HTTP сервер: Ошибка", foreground="red"))
                else:
                    # Если сервер остановился без ошибок (например, по Ctrl+C в его окне)
                    self.root.after(0, lambda: self.server_status_label.config(text="HTTP сервер: Остановлен", foreground="red"))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"❌ Ошибка мониторинга сервера: {e}"))
                
    def open_chat_browser(self):
        url = f"http://localhost:{self.settings['server_port']}/vmix_simple.html"
        webbrowser.open(url)
        self.log(f"🌐 Открыт чат в браузере: {url}")
    
    def open_theme_demo(self):
        """Открывает демонстрацию тем"""
        url = f"http://localhost:{self.settings['server_port']}/theme_demo.html"
        webbrowser.open(url)
        self.log(f"🎨 Открыта демонстрация тем: {url}")
        
    def open_project_folder(self):
        project_path = os.path.dirname(os.path.abspath(__file__))
        os.startfile(project_path)
        
    def clear_chat(self):
        """Очищает все сообщения в чате"""
        try:
            # Очищаем messages.json
            with open('messages.json', 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            
            # Удаляем файл последнего URL чтобы принудительно очистить при следующем запуске
            if os.path.exists('last_stream_url.txt'):
                os.remove('last_stream_url.txt')
                
            self.log("🧹 Чат очищен! Все старые сообщения удалены")
            messagebox.showinfo("Успех", "Чат успешно очищен!\nВсе старые сообщения удалены.")
            
        except Exception as e:
            self.log(f"❌ Ошибка очистки чата: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось очистить чат:\n{str(e)}")
    
    def restart_parser(self):
        """Перезапускает парсер чата"""
        if not self.settings.get('video_url'):
            messagebox.showwarning("Предупреждение", "Сначала введите URL трансляции")
            return
            
        self.log("🔄 Перезапуск парсера...")
        self.stop_parser()
        
        # Небольшая задержка перед запуском
        self.root.after(1000, self.start_parser)
    
    def test_parser(self):
        """Тестирует работоспособность парсера"""
        self.log("🧪 Запуск тестирования парсера...")
        
        def run_test():
            try:
                # Запускаем тест парсера
                result = subprocess.run(
                    ["python", "test_parser.py"],
                    capture_output=True,
                    text=True,
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )
                
                # Выводим результат в лог
                if result.stdout:
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            self.root.after(0, lambda l=line: self.log(l))
                
                if result.stderr:
                    for line in result.stderr.split('\n'):
                        if line.strip():
                            self.root.after(0, lambda l=line: self.log(f"❌ {l}"))
                
                if result.returncode == 0:
                    self.root.after(0, lambda: self.log("✅ Тестирование завершено успешно"))
                else:
                    self.root.after(0, lambda: self.log("❌ Тестирование завершено с ошибками"))
                    
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.log(f"❌ Ошибка тестирования: {error_msg}"))
        
        # Запускаем тест в отдельном потоке
        threading.Thread(target=run_test, daemon=True).start()
    
    def paste_url(self, event):
        """Вставляет текст из буфера обмена в поле URL"""
        try:
            clipboard_text = self.root.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard_text)
            self.log(f"📋 URL вставлен из буфера: {clipboard_text[:50]}...")
            return 'break'  # Предотвращаем стандартную обработку
        except tk.TclError:
            self.log("❌ Буфер обмена пуст или недоступен")
            return 'break'
    
    def select_all_url(self, event):
        """Выделяет весь текст в поле URL"""
        self.url_entry.select_range(0, tk.END)
        return 'break'
    
    def copy_url(self, event):
        """Копирует выделенный текст в буфер обмена"""
        try:
            if self.url_entry.selection_present():
                selected_text = self.url_entry.selection_get()
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                self.log("📋 Текст скопирован в буфер")
            else:
                # Если ничего не выделено, копируем весь URL
                url_text = self.url_var.get()
                self.root.clipboard_clear()
                self.root.clipboard_append(url_text)
                self.log("📋 URL скопирован в буфер")
            return 'break'
        except tk.TclError:
            pass
    
    def cut_url(self, event):
        """Вырезает выделенный текст в буфер обмена"""
        try:
            if self.url_entry.selection_present():
                selected_text = self.url_entry.selection_get()
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                self.url_entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
                self.log("📋 Текст вырезан в буфер")
            return 'break'
        except tk.TclError:
            pass
    
    def paste_from_clipboard(self):
        """Кнопка для вставки URL из буфера обмена"""
        try:
            clipboard_text = self.root.clipboard_get().strip()
            self.url_var.set(clipboard_text)
            self.log(f"📋 URL вставлен из буфера: {clipboard_text[:50]}...")
            # Автоматически проверяем URL после вставки
            self.validate_url()
        except tk.TclError:
            self.log("❌ Буфер обмена пуст или недоступен")
            messagebox.showwarning("Предупреждение", "Буфер обмена пуст или недоступен")
    
    def clear_url(self):
        """Очищает поле URL"""
        self.url_var.set("")
        self.url_status_label.config(text="", foreground="gray")
        self.log("🧹 Поле URL очищено")
        
    def apply_settings(self):
        """Применяет настройки и обновляет файлы"""
        # Обновляем настройки из GUI
        self.settings.update({
            'chat_width': self.width_var.get(),
            'chat_height': self.height_var.get(),
            'chat_position_x': self.pos_x_var.get(),
            'chat_position_y': self.pos_y_var.get(),
            'font_size': self.font_size_var.get(),
            'message_lifetime': self.lifetime_var.get(),
            'max_messages': self.max_msg_var.get(),
            'show_avatars': self.show_avatars_var.get(),
            'fade_effect': self.fade_effect_var.get(),
            'highlight_sponsors': self.highlight_sponsors_var.get(),
            'show_user_badges': self.show_badges_var.get(),
            'server_port': self.port_var.get(),
            'video_url': self.url_var.get().strip(),
            'theme': self.theme_var.get()
        })
        
        self.save_settings()
        self.update_css_file()
        self.log("💾 Настройки применены")
        
    def save_settings(self):
        """Сохраняет настройки в файл"""
        try:
            with open('chat_settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log(f"❌ Ошибка сохранения настроек: {e}")
            
    def update_css_file(self):
        """Обновляет CSS файл с новыми настройками"""
        css_content = f"""body {{
    margin: 0;
    padding: 0;
    background: transparent;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    overflow: hidden;
}}

#chat {{
    position: fixed;
    left: {self.settings['chat_position_x']};
    bottom: {self.settings['chat_position_y']};
    width: {self.settings['chat_width']};
    height: {self.settings['chat_height']};
    max-width: 1500px;
    min-width: 780px;
    background: transparent;
    color: white;
    font-size: {self.settings['font_size']};
    font-weight: bold;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    overflow-y: auto;
    overflow-x: hidden;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    scrollbar-width: none;
    -ms-overflow-style: none;
    {"mask: linear-gradient(to bottom, transparent, white 20%, white);" if self.settings['fade_effect'] else ""}
    {"background: linear-gradient(to bottom, transparent, rgba(0,0,0,0.1) 20%, rgba(0,0,0,0.2));" if self.settings['fade_effect'] else ""}
}}

#chat::-webkit-scrollbar {{
    display: none;
}}

.message {{
    display: flex;
    align-items: center; /* Выравнивание по центру по вертикали */
    margin: 0.3em 0;
    padding: 0.2em 0;
    word-wrap: break-word;
    line-height: 1.2;
    animation: fadeIn 0.5s ease-in;
    {"opacity: 0.95;" if self.settings['fade_effect'] else ""}
}}

.message img {{
    {"display: inline;" if self.settings['show_avatars'] else "display: none;"}
}}

.avatar {{
    width: 32px !important;
    height: 32px !important;
    border-radius: 50% !important;
    object-fit: cover !important;
    box-shadow: 0 0 4px rgba(0,0,0,0.5) !important; /* Меньшая тень */
    margin-right: 8px !important; /* Меньший отступ */
    vertical-align: middle !important;
}}

.message-content {{
    display: flex;
    flex-direction: row; /* Содержимое сообщения в строку */
    align-items: center; /* Выравнивание по центру по вертикали */
}}

.author-name {{
    font-weight: bold;
    color: #ffdd44; /* Пример цвета, можно настроить */
    margin-right: 0.5em; /* Отступ между именем и текстом */
}}

.message-text {{
    /* Нет необходимости в margin-left, так как author-name имеет margin-right */
}}

@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes fadeOut {{
    from {{ opacity: 1; transform: translateY(0); }}
    to {{ opacity: 0; transform: translateY(-20px); }}
}}
"""
        
        try:
            with open('style.css', 'w', encoding='utf-8') as f:
                f.write(css_content)
        except Exception as e:
            self.log(f"❌ Ошибка обновления CSS: {e}")
            
    def load_settings(self):
        try:
            if os.path.exists('chat_settings.json'):
                with open('chat_settings.json', 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
        except Exception as e:
            self.log(f"⚠️ Не удалось загрузить настройки: {str(e)}")
            
    def reset_settings(self):
        # Возвращаем настройки по умолчанию
        default_settings = {
            'chat_width': '84vw',
            'chat_height': '92vh',
            'chat_position_x': '2vw',
            'chat_position_y': '8vh',
            'font_size': '2.8em',
            'message_lifetime': 900,
            'max_messages': 50,
            'show_avatars': True,
            'fade_effect': True,
            'server_port': 8080,
            'update_interval': 1
        }
        
        self.settings.update(default_settings)
        
        # Обновляем GUI
        self.width_var.set(default_settings['chat_width'])
        self.height_var.set(default_settings['chat_height'])
        self.pos_x_var.set(default_settings['chat_position_x'])
        self.pos_y_var.set(default_settings['chat_position_y'])
        self.font_size_var.set(default_settings['font_size'])
        self.lifetime_var.set(default_settings['message_lifetime'])
        self.max_msg_var.set(default_settings['max_messages'])
        self.show_avatars_var.set(default_settings['show_avatars'])
        self.fade_effect_var.set(default_settings['fade_effect'])
        self.port_var.set(default_settings['server_port'])
        
        self.log("🔄 Настройки сброшены к значениям по умолчанию")
        
    def log(self, message):
        """Добавляет сообщение в лог и в файл gui.log"""
        # Инициализируем файл лога при первом вызове
        if not hasattr(self, 'log_file_initialized'):
            self.log_file = "gui.log"
            try:
                with open(self.log_file, "w", encoding="utf-8") as f:
                    f.write(f"--- GUI Log Started at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                self.log_file_initialized = True
            except Exception:
                self.log_file_initialized = False

        import datetime
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        
        cleaned_message = str(message).strip()
        
        # Выводим в текстовое поле в GUI
        self.log_text.insert(tk.END, f"[{timestamp}] {cleaned_message}\n")
        self.log_text.see(tk.END)

        # Записываем в файл
        if getattr(self, 'log_file_initialized', False):
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] {cleaned_message}\n")
            except Exception:
                pass
        
    def clear_logs(self):
        self.log_text.delete(1.0, tk.END)
        
    def on_closing(self):
        """Обработчик закрытия приложения"""
        self.stop_all()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    
    app = YouTubeChatGUISimple(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop() 