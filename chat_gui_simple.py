#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess
import threading
import webbrowser
import time

def setup_logging():
    """Настраивает детальное логирование в файл"""
    log_file = 'gui_debug.log'
    # Очищаем файл лога при старте
    if os.path.exists(log_file):
        os.remove(log_file)
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler() # Также выводим в консоль
        ]
    )
    logging.info("Логирование настроено.")

class YouTubeChatGUISimple:
    def __init__(self, root):
        logging.info("Инициализация YouTubeChatGUISimple...")
        self.root = root
        self.root.title("YouTube Live Chat Overlay - Управление")
        self.root.geometry("850x700") # Немного увеличим размер
        
        # Переменные для процессов
        self.parser_process = None
        self.server_process = None
        
        # Словарь для отслеживания процессов отдельных каналов
        # Ключ: префикс канала, Значение: subprocess.Popen объект
        self.channel_processes = {}
        
        # Настройки по умолчанию
        self.settings = {}
        self.load_default_settings()
        
        logging.info("Вызов load_settings()...")
        try:
            self.load_settings()
            logging.info("load_settings() завершен успешно.")
        except Exception as e:
            logging.error(f"ОШИБКА в load_settings(): {e}", exc_info=True)
            raise
        
        logging.info("Вызов create_gui()...")
        try:
            self.create_gui()
            logging.info("create_gui() завершен успешно.")
        except Exception as e:
            logging.error(f"ОШИБКА в create_gui(): {e}", exc_info=True)
            raise
        
        logging.info("Инициализация YouTubeChatGUISimple завершена.")
        
    def start_status_checker(self):
        """Запускает периодическую проверку статуса процессов"""
        logging.info("Запуск периодической проверки статуса.")
        self.check_process_status()

    def check_process_status(self):
        """Проверяет и обновляет статус парсера и сервера"""
        try:
            logging.debug("Проверка статуса процессов...")
            # Проверка парсера
            if self.parser_process and self.parser_process.poll() is None:
                self.parser_status_label.config(text="Парсер чата: Работает", foreground="green")
            else:
                self.parser_status_label.config(text="Парсер чата: Остановлен", foreground="red")

            # Проверка сервера
            if self.server_process and self.server_process.poll() is None:
                self.server_status_label.config(text="HTTP сервер: Работает", foreground="green")
            else:
                self.server_status_label.config(text="HTTP сервер: Остановлен", foreground="red")
            
            logging.debug("Статус процессов обновлен.")
        except Exception as e:
            logging.error(f"Ошибка в check_process_status: {e}", exc_info=True)
        
        # Повторяем проверку через 2 секунды
        self.root.after(2000, self.check_process_status)
        
    def load_default_settings(self):
        logging.debug("Загрузка настроек по умолчанию...")
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
            'theme': 'barbie',
            'multichat_enabled': False,
            'multichat_channels': [],
            'performance_optimization_enabled': False,
            'max_messages_per_channel_per_cycle': 10,
            'message_processing_delay': 0.1,
            'auto_performance_protection': True
        }
        logging.debug("Настройки по умолчанию загружены.")
        
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
        
    def create_gui(self):
        # Главный фрейм с вкладками
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка 1: Мульти-чат
        multichat_frame = ttk.Frame(notebook)
        notebook.add(multichat_frame, text="Мульти-чат")
        self.create_multichat_tab(multichat_frame)
        
        # Вкладка 2: Настройки отображения
        display_frame = ttk.Frame(notebook)
        notebook.add(display_frame, text="Настройки отображения")
        self.create_display_tab(display_frame)
        
        # Вкладка 3: Управление
        control_frame = ttk.Frame(notebook)
        notebook.add(control_frame, text="Управление")
        self.create_control_tab(control_frame)
        
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
        
    def create_multichat_tab(self, parent):
        # Включение мульти-чата
        multichat_enable_group = ttk.LabelFrame(parent, text="Режим мульти-чата", padding=10)
        multichat_enable_group.pack(fill='x', padx=10, pady=5)
        
        self.multichat_enabled_var = tk.BooleanVar(value=self.settings.get('multichat_enabled', False))
        ttk.Checkbutton(multichat_enable_group, text="Включить мульти-чат (несколько YouTube каналов одновременно)", 
                       variable=self.multichat_enabled_var, command=self.toggle_multichat).pack(anchor='w')
        
        ttk.Label(multichat_enable_group, text="При включении мульти-чата сообщения из всех каналов будут объединены с префиксами [YT1], [YT2] и т.д.", 
                 foreground="gray", wraplength=600).pack(anchor='w', pady=(5,0))
        
        # Список каналов
        channels_group = ttk.LabelFrame(parent, text="YouTube каналы", padding=10)
        channels_group.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Фрейм для списка каналов
        channels_list_frame = ttk.Frame(channels_group)
        channels_list_frame.pack(fill='both', expand=True, pady=(0,10))
        
        # Создаем Treeview для отображения каналов
        columns = ('status', 'prefix', 'name', 'url')
        self.channels_tree = ttk.Treeview(channels_list_frame, columns=columns, show='headings', height=6)
        
        # Настройка заголовков
        self.channels_tree.heading('status', text='●')
        self.channels_tree.heading('prefix', text='Префикс')
        self.channels_tree.heading('name', text='Название канала')
        self.channels_tree.heading('url', text='URL трансляции')
        
        # Настройка ширины колонок
        self.channels_tree.column('status', width=60, minwidth=60, anchor='center')
        self.channels_tree.column('prefix', width=80, minwidth=60)
        self.channels_tree.column('name', width=150, minwidth=100)
        self.channels_tree.column('url', width=280, minwidth=200)
        
        # Скроллбар для списка
        channels_scrollbar = ttk.Scrollbar(channels_list_frame, orient="vertical", command=self.channels_tree.yview)
        self.channels_tree.configure(yscrollcommand=channels_scrollbar.set)
        
        # Настройка тегов для раскраски статусов
        self.channels_tree.tag_configure('running', foreground='green')
        self.channels_tree.tag_configure('stopped', foreground='red')
        
        self.channels_tree.pack(side='left', fill='both', expand=True)
        channels_scrollbar.pack(side='right', fill='y')
        
        # Кнопки управления каналами
        channels_buttons_frame = ttk.Frame(channels_group)
        channels_buttons_frame.pack(fill='x')
        
        # Левая сторона - управление списком
        left_buttons = ttk.Frame(channels_buttons_frame)
        left_buttons.pack(side='left')
        ttk.Button(left_buttons, text="➕ Добавить канал", command=self.add_channel).pack(side='left', padx=(0,5))
        ttk.Button(left_buttons, text="✏️ Редактировать", command=self.edit_channel).pack(side='left', padx=5)
        ttk.Button(left_buttons, text="🗑️ Удалить", command=self.remove_channel).pack(side='left', padx=5)
        
        # Правая сторона - управление отдельными каналами
        right_buttons = ttk.Frame(channels_buttons_frame)
        right_buttons.pack(side='right')
        ttk.Button(right_buttons, text="✅ Включить канал", command=self.start_selected_channel).pack(side='left', padx=5)
        ttk.Button(right_buttons, text="⭕ Выключить канал", command=self.stop_selected_channel).pack(side='left', padx=5)
        ttk.Button(right_buttons, text="📋 Логи", command=self.show_multichat_logs).pack(side='left', padx=(5,0))
        
        # Настройки производительности (опциональные)
        performance_group = ttk.LabelFrame(parent, text="⚡ Настройки производительности (для высоконагруженных каналов)", padding=10)
        performance_group.pack(fill='x', padx=10, pady=5)
        
        # Включение настроек производительности
        self.performance_enabled_var = tk.BooleanVar(value=self.settings.get('performance_optimization_enabled', False))
        performance_checkbox = ttk.Checkbutton(performance_group, text="🔧 Включить оптимизацию производительности", 
                                             variable=self.performance_enabled_var, command=lambda: self.toggle_performance_settings(log_action=True))
        performance_checkbox.pack(anchor='w', pady=(0,5))
        
        # Информация о лимитах в мульти-чате
        info_label = ttk.Label(performance_group, 
                              text="ℹ️ В мульти-чате лимит сообщений автоматически увеличивается пропорционально количеству каналов", 
                              foreground="gray", font=('TkDefaultFont', 8), wraplength=500)
        info_label.pack(anchor='w', pady=(0,10))
        
        # Фрейм для настроек производительности
        self.performance_settings_frame = ttk.Frame(performance_group)
        self.performance_settings_frame.pack(fill='x')
        
        # Максимум сообщений на канал за цикл
        ttk.Label(self.performance_settings_frame, text="Макс. сообщений на канал за цикл:").pack(anchor='w')
        self.max_messages_per_channel_var = tk.StringVar(value=str(self.settings.get('max_messages_per_channel_per_cycle', 10)))
        messages_frame = ttk.Frame(self.performance_settings_frame)
        messages_frame.pack(fill='x', pady=5)
        ttk.Entry(messages_frame, textvariable=self.max_messages_per_channel_var, width=10).pack(side='left')
        ttk.Label(messages_frame, text="(меньше = стабильнее, больше = быстрее)", foreground="gray").pack(side='left', padx=(5,0))
        
        # Задержка обработки
        ttk.Label(self.performance_settings_frame, text="Задержка обработки (сек):").pack(anchor='w', pady=(10,0))
        self.processing_delay_var = tk.StringVar(value=str(self.settings.get('message_processing_delay', 0.0)))
        delay_frame = ttk.Frame(self.performance_settings_frame)
        delay_frame.pack(fill='x', pady=5)
        ttk.Entry(delay_frame, textvariable=self.processing_delay_var, width=10).pack(side='left')
        ttk.Label(delay_frame, text="(0.0 = максимальная скорость, 0.1+ = стабильность)", foreground="gray").pack(side='left', padx=(5,0))
        
        # Автоматическая защита
        ttk.Label(self.performance_settings_frame, text="Автоматическая защита:").pack(anchor='w', pady=(10,0))
        self.auto_protection_var = tk.BooleanVar(value=self.settings.get('auto_performance_protection', True))
        auto_protection_checkbox = ttk.Checkbutton(self.performance_settings_frame, 
                                                  text="🛡️ Автоматически включать оптимизацию при критической нагрузке", 
                                                  variable=self.auto_protection_var)
        auto_protection_checkbox.pack(anchor='w', pady=5)
        
        # Подсказка
        help_label = ttk.Label(self.performance_settings_frame, 
                              text="💡 Включайте оптимизацию если каналы часто отключаются при высокой нагрузке", 
                              foreground="blue", font=('TkDefaultFont', 8))
        help_label.pack(anchor='w', pady=(10,0))
        
        # Изначально скрываем настройки если не включены (без логирования)
        self.toggle_performance_settings(log_action=False)
        
        # Загружаем существующие каналы
        self.load_channels()
        
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
        ttk.Button(button_frame1, text="🔐 OAuth авторизация", command=self.oauth_authorization).pack(side='left', padx=5)
        
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
        
        # Запускаем проверку статуса ПОСЛЕ создания всех элементов
        self.start_status_checker()
    
        
    def start_all(self):
        # Проверяем, включён ли мульти-чат
        if self.settings.get('multichat_enabled', False):
            # В режиме мульти-чата URL берутся из списка каналов
            channels = self.settings.get('multichat_channels', [])
            if not channels:
                messagebox.showwarning("Предупреждение", "Добавьте хотя бы один канал в мульти-чате")
                return
        else:
            # В обычном режиме нужен URL (но сейчас обычный режим не используется)
            if not self.settings.get('video_url'):
                messagebox.showwarning("Предупреждение", "Включите мульти-чат и добавьте каналы")
                return
            
        self.apply_settings()  # Применяем настройки перед запуском
        self.start_server()
        self.start_parser()
        
    def start_parser(self):
        # Проверяем, включён ли мульти-чат
        if self.settings.get('multichat_enabled', False):
            self.start_multichat()
            return
        
        # Обычный режим больше не поддерживается, всегда используем мульти-чат
        messagebox.showwarning("Предупреждение", "Включите режим мульти-чата и добавьте каналы во вкладке 'Мульти-чат'")
        return
            
        if self.parser_process and self.parser_process.poll() is None:
            self.log("⚠️ Парсер уже запущен")
            return
            
        try:
            # Проверяем наличие OAuth токенов
            oauth_token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "youtube_oauth_token.json")
            if not os.path.exists(oauth_token_file):
                self.log("⚠️ ВНИМАНИЕ: OAuth авторизация не пройдена!")
                self.log("📝 Для работы парсера нужна OAuth авторизация YouTube")
                self.log("💡 Запустите: AUTHORIZE_YOUTUBE.bat или используйте опцию 2 в START.bat")
                
                response = messagebox.askyesno(
                    "OAuth авторизация требуется",
                    "Для стабильной работы парсера нужна OAuth авторизация YouTube.\n\n"
                    "Пройти авторизацию сейчас?\n\n"
                    "(Откроется браузер для входа в аккаунт YouTube)"
                )
                
                if response:
                    # Запускаем OAuth авторизацию
                    venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "python.exe")
                    subprocess.Popen([venv_python, "youtube_auth.py"], env=self.get_clean_env())
                    self.log("🔐 Запущена OAuth авторизация. После завершения попробуйте запустить парсер снова.")
                return
            
            self.log("🚀 Запуск парсера чата с OAuth...")
            
            # Запускаем парсер через venv Python
            venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "python.exe")
            
            self.parser_process = subprocess.Popen(
                [venv_python, "chat_parser_oauth.py", self.settings['video_url']],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                env=self.get_clean_env()
            )
            
            self.parser_status_label.config(text="Парсер чата: Работает (OAuth)", foreground="green")
            self.log("✅ Парсер чата запущен с OAuth авторизацией")
            
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
                cwd=os.path.dirname(os.path.abspath(__file__)),
                env=self.get_clean_env()
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
    
    def oauth_authorization(self):
        """Запускает OAuth авторизацию YouTube"""
        self.log("🔐 Запуск OAuth авторизации YouTube...")
        
        try:
            venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "python.exe")
            auth_process = subprocess.Popen([venv_python, "youtube_auth.py"], env=self.get_clean_env())
            
            self.log("🌐 Откроется браузер для авторизации")
            self.log("📝 Следуйте инструкциям в браузере:")
            self.log("   1. Войдите в аккаунт YouTube/Google")
            self.log("   2. Разрешите доступ к YouTube API")
            self.log("   3. После успешной авторизации закройте окно")
            
            # Ждем завершения авторизации
            def check_auth_completion():
                auth_process.wait()
                oauth_token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "youtube_oauth_token.json")
                if os.path.exists(oauth_token_file):
                    self.log("✅ OAuth авторизация успешно завершена!")
                    self.log("🎉 Теперь можете запускать парсер")
                else:
                    self.log("⚠️ OAuth авторизация не завершена или отменена")
            
            threading.Thread(target=check_auth_completion, daemon=True).start()
            
        except Exception as e:
            self.log(f"❌ Ошибка запуска OAuth авторизации: {str(e)}")
            
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
                error_msg = str(e)
                self.root.after(0, lambda: self.log(f"❌ Ошибка мониторинга сервера: {error_msg}"))
                
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
                # Запускаем тест парсера через venv Python
                venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "python.exe")
                result = subprocess.run(
                    [venv_python, "test_parser.py"],
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
    
    
    def setup_entry_bindings(self, entry_widget):
        """Настраивает горячие клавиши для поля ввода"""
        # Стандартные горячие клавиши
        entry_widget.bind('<Control-v>', lambda e: self.paste_to_widget(entry_widget))
        entry_widget.bind('<Control-V>', lambda e: self.paste_to_widget(entry_widget))
        entry_widget.bind('<Control-a>', lambda e: self.select_all_widget(entry_widget))
        entry_widget.bind('<Control-A>', lambda e: self.select_all_widget(entry_widget))
        entry_widget.bind('<Control-c>', lambda e: self.copy_from_widget(entry_widget))
        entry_widget.bind('<Control-C>', lambda e: self.copy_from_widget(entry_widget))
        entry_widget.bind('<Control-x>', lambda e: self.cut_from_widget(entry_widget))
        entry_widget.bind('<Control-X>', lambda e: self.cut_from_widget(entry_widget))
    
    def paste_to_widget(self, widget):
        """Вставляет текст из буфера в виджет"""
        try:
            # Пытаемся получить clipboard от родительского окна виджета
            parent_window = widget.winfo_toplevel()
            clipboard_text = parent_window.clipboard_get().strip()
            widget.delete(0, tk.END)
            widget.insert(0, clipboard_text)
            print(f"📋 Текст вставлен в поле: {clipboard_text[:50]}...")
            return 'break'
        except tk.TclError:
            print("❌ Буфер обмена пуст или недоступен")
            return 'break'
    
    def select_all_widget(self, widget):
        """Выделяет весь текст в виджете"""
        widget.select_range(0, tk.END)
        return 'break'
    
    def copy_from_widget(self, widget):
        """Копирует выделенный текст из виджета"""
        try:
            if widget.selection_present():
                selected_text = widget.selection_get()
            else:
                selected_text = widget.get()
            
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
            return 'break'
        except tk.TclError:
            return 'break'
    
    def cut_from_widget(self, widget):
        """Вырезает выделенный текст из виджета"""
        try:
            if widget.selection_present():
                selected_text = widget.selection_get()
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            return 'break'
        except tk.TclError:
            return 'break'
    
    def paste_to_entry(self, string_var):
        """Вставляет текст из буфера в StringVar"""
        try:
            clipboard_text = self.root.clipboard_get().strip()
            string_var.set(clipboard_text)
            self.log(f"📋 URL вставлен: {clipboard_text[:50]}...")
        except tk.TclError:
            self.log("❌ Буфер обмена пуст")
            messagebox.showwarning("Предупреждение", "Буфер обмена пуст или недоступен")
        
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
            'theme': self.theme_var.get()
        })
        
        # Добавляем настройки производительности мульти-чата (только если включены)
        if hasattr(self, 'performance_enabled_var'):
            self.settings['performance_optimization_enabled'] = self.performance_enabled_var.get()
            
            # Сохраняем настройки производительности только если они включены
            if self.performance_enabled_var.get():
                if hasattr(self, 'max_messages_per_channel_var'):
                    try:
                        self.settings['max_messages_per_channel_per_cycle'] = int(self.max_messages_per_channel_var.get())
                    except ValueError:
                        self.settings['max_messages_per_channel_per_cycle'] = 10
                
                if hasattr(self, 'processing_delay_var'):
                    try:
                        self.settings['message_processing_delay'] = float(self.processing_delay_var.get())
                    except ValueError:
                        self.settings['message_processing_delay'] = 0.0
                
                # Сохраняем настройку автоматической защиты
                if hasattr(self, 'auto_protection_var'):
                    self.settings['auto_performance_protection'] = self.auto_protection_var.get()
        
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
        
    # =============================================================================
    # МЕТОДЫ ДЛЯ МУЛЬТИ-ЧАТА
    # =============================================================================
    
    def toggle_multichat(self):
        """Переключение режима мульти-чата"""
        enabled = self.multichat_enabled_var.get()
        self.settings['multichat_enabled'] = enabled
        self.save_settings()
        
        if enabled:
            self.log("🔄 Режим мульти-чата включён")
        else:
            self.log("🔄 Режим мульти-чата отключён")
    
    def toggle_performance_settings(self, log_action=True):
        """Переключает видимость настроек производительности"""
        enabled = self.performance_enabled_var.get()
        
        if enabled:
            # Показываем настройки
            for child in self.performance_settings_frame.winfo_children():
                child.pack_configure()
            if log_action and hasattr(self, 'log_text'):
                self.log("⚡ Оптимизация производительности включена")
        else:
            # Скрываем настройки
            for child in self.performance_settings_frame.winfo_children():
                child.pack_forget()
            if log_action and hasattr(self, 'log_text'):
                self.log("⚡ Оптимизация производительности отключена")
        
        # Сохраняем состояние только если GUI полностью инициализирован
        if hasattr(self, 'settings'):
            self.settings['performance_optimization_enabled'] = enabled
            if hasattr(self, 'log_text'):  # Сохраняем только если GUI готов
                self.save_settings()
    
    def load_channels(self):
        """Загружает список каналов в таблицу"""
        # Очищаем таблицу
        for item in self.channels_tree.get_children():
            self.channels_tree.delete(item)
        
        # Загружаем каналы из настроек
        channels = self.settings.get('multichat_channels', [])
        for i, channel in enumerate(channels):
            prefix = channel.get('prefix', f'[YT{i+1}]')
            name = channel.get('name', f'Канал {i+1}')
            url = channel.get('url', '')
            
            # Проверяем статус канала и определяем тег
            is_running, status_text = self.get_channel_status(prefix)
            tag = 'running' if is_running else 'stopped'
            
            # Вставляем строку с тегом для раскраски
            self.channels_tree.insert('', 'end', values=(status_text, prefix, name, url), tags=(tag,))
    
    def get_channel_status(self, prefix):
        """Возвращает статус канала и текст для отображения"""
        # Ищем канал в настройках
        channels = self.settings.get('multichat_channels', [])
        for channel in channels:
            if channel.get('prefix') == prefix:
                enabled = channel.get('enabled', False)
                if enabled:
                    return True, "● ON"
                else:
                    return False, "● OFF"
        return False, "● OFF"
    
    def add_channel(self):
        """Добавляет новый канал"""
        self.edit_channel_dialog()
    
    def edit_channel(self):
        """Редактирует выбранный канал"""
        selected = self.channels_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите канал для редактирования")
            return
        
        item = self.channels_tree.item(selected[0])
        values = item['values']
        
        # Пропускаем первое значение (статус) и передаем остальные
        self.edit_channel_dialog(values[1:])
    
    def edit_channel_dialog(self, existing_values=None):
        """Диалог добавления/редактирования канала"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить канал" if not existing_values else "Редактировать канал")
        dialog.geometry("600x400")  # Увеличиваем размер окна
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(True, False)  # Разрешаем изменение ширины
        
        # Центрируем диалог
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Поля ввода
        ttk.Label(dialog, text="Префикс канала:").pack(anchor='w', padx=10, pady=(10,0))
        prefix_var = tk.StringVar(value=existing_values[0] if existing_values else f'[YT{len(self.settings.get("multichat_channels", [])) + 1}]')
        prefix_entry = ttk.Entry(dialog, textvariable=prefix_var, width=50)
        prefix_entry.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(dialog, text="Название канала:").pack(anchor='w', padx=10, pady=(10,0))
        name_var = tk.StringVar(value=existing_values[1] if existing_values else '')
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=50)
        name_entry.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(dialog, text="URL трансляции:").pack(anchor='w', padx=10, pady=(10,0))
        url_var = tk.StringVar(value=existing_values[2] if existing_values else '')
        url_entry = ttk.Entry(dialog, textvariable=url_var, width=50)
        url_entry.pack(fill='x', padx=10, pady=5)
        
        # Добавляем поддержку горячих клавиш для URL поля в диалоге
        self.setup_entry_bindings(url_entry)
        
        # Кнопка для быстрой вставки URL
        paste_frame = ttk.Frame(dialog)
        paste_frame.pack(fill='x', padx=10, pady=(0,5))
        
        def paste_url_to_dialog():
            """Вставляет URL из буфера в диалог"""
            try:
                clipboard_text = dialog.clipboard_get().strip()
                url_var.set(clipboard_text)
                print(f"📋 URL вставлен в диалог: {clipboard_text[:50]}...")
            except tk.TclError:
                messagebox.showwarning("Предупреждение", "Буфер обмена пуст или недоступен")
        
        ttk.Button(paste_frame, text="📋 Вставить URL из буфера (Ctrl+V)", 
                  command=paste_url_to_dialog).pack(side='right')
        
        # Инструкции и примеры
        help_text = """Примеры URL:
• https://www.youtube.com/watch?v=VIDEO_ID
• https://youtube.com/live/VIDEO_ID

💡 Горячие клавиши в поле URL:
• Ctrl+V - Вставить из буфера
• Ctrl+A - Выделить всё
• Ctrl+C - Копировать"""
        
        ttk.Label(dialog, text=help_text, foreground="gray", justify='left').pack(anchor='w', padx=10, pady=(5,15))
        
        # Кнопки
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        def save_channel():
            prefix = prefix_var.get().strip()
            name = name_var.get().strip()
            url = url_var.get().strip()
            
            if not prefix or not name or not url:
                messagebox.showwarning("Предупреждение", "Заполните все поля")
                return
            
            # Проверяем уникальность префикса
            channels = self.settings.get('multichat_channels', [])
            for i, channel in enumerate(channels):
                if existing_values and i == self.channels_tree.index(self.channels_tree.selection()[0]):
                    continue  # Пропускаем текущий канал при редактировании
                if channel.get('prefix') == prefix:
                    messagebox.showwarning("Предупреждение", f"Префикс {prefix} уже используется")
                    return
            
            channel_data = {
                'prefix': prefix,
                'name': name,
                'url': url,
                'enabled': channel.get('enabled', False) if existing_values else False  # При создании нового - выключен
            }
            
            if existing_values:
                # Редактирование
                selected_index = self.channels_tree.index(self.channels_tree.selection()[0])
                channels[selected_index] = channel_data
                self.log(f"✏️ Канал {name} обновлён")
            else:
                # Добавление
                channels.append(channel_data)
                self.log(f"➕ Добавлен канал {name}")
            
            self.settings['multichat_channels'] = channels
            self.save_settings()
            self.load_channels()
            dialog.destroy()
        
        # Кнопки с отступами для лучшей видимости
        ttk.Button(button_frame, text="✅ Сохранить", command=save_channel).pack(side='left', padx=(0,10))
        ttk.Button(button_frame, text="❌ Отмена", command=dialog.destroy).pack(side='right', padx=(10,0))
        
        # Добавляем разделитель для лучшей видимости кнопок
        separator = ttk.Separator(dialog, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=(5,0))
    
    def remove_channel(self):
        """Удаляет выбранный канал"""
        selected = self.channels_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите канал для удаления")
            return
        
        item = self.channels_tree.item(selected[0])
        values = item['values']
        prefix = values[1]  # Префикс на позиции 1 (после статуса)
        channel_name = values[2]  # Название на позиции 2
        
        # Проверяем, не включен ли канал
        channels = self.settings.get('multichat_channels', [])
        selected_index = self.channels_tree.index(selected[0])
        if 0 <= selected_index < len(channels):
            if channels[selected_index].get('enabled', False):
                messagebox.showwarning("Предупреждение", 
                    f"Канал '{channel_name}' включен.\nВыключите его перед удалением.")
                return
        
        if messagebox.askyesno("Подтверждение", f"Удалить канал '{channel_name}'?"):
            del channels[selected_index]
            self.settings['multichat_channels'] = channels
            self.save_settings()
            self.load_channels()
            self.log(f"🗑️ Канал {channel_name} удалён")
    
    
    def show_multichat_logs(self):
        """Показывает логи мульти-чата в отдельном окне"""
        log_window = tk.Toplevel(self.root)
        log_window.title("Логи мульти-чата")
        log_window.geometry("800x600")
        log_window.transient(self.root)
        
        # Центрируем окно
        log_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 50))
        
        # Создаем текстовое поле с прокруткой
        log_frame = ttk.Frame(log_window)
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        log_text = tk.Text(log_frame, wrap='word', font=('Consolas', 9))
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=log_text.yview)
        log_text.configure(yscrollcommand=log_scrollbar.set)
        
        log_text.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')
        
        # Кнопки управления
        button_frame = ttk.Frame(log_window)
        button_frame.pack(fill='x', padx=10, pady=(0,10))
        
        def refresh_logs():
            """Обновляет содержимое логов"""
            log_text.delete(1.0, tk.END)
            
            # Читаем лог мульти-чата
            try:
                with open('multichat.log', 'r', encoding='utf-8') as f:
                    content = f.read()
                    log_text.insert(tk.END, content)
                    log_text.see(tk.END)  # Прокручиваем в конец
            except FileNotFoundError:
                log_text.insert(tk.END, "Лог файл мульти-чата не найден.\nВозможно, мульти-чат ещё не запускался.")
            except Exception as e:
                log_text.insert(tk.END, f"Ошибка чтения лог файла: {e}")
        
        def clear_logs():
            """Очищает лог файл"""
            try:
                with open('multichat.log', 'w', encoding='utf-8') as f:
                    f.write("")
                refresh_logs()
                self.log("🧹 Логи мульти-чата очищены")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось очистить логи: {e}")
        
        ttk.Button(button_frame, text="🔄 Обновить", command=refresh_logs).pack(side='left')
        ttk.Button(button_frame, text="🧹 Очистить логи", command=clear_logs).pack(side='left', padx=(5,0))
        ttk.Button(button_frame, text="❌ Закрыть", command=log_window.destroy).pack(side='right')
        
        # Автообновление каждые 5 секунд
        def auto_refresh():
            if log_window.winfo_exists():
                refresh_logs()
                log_window.after(5000, auto_refresh)  # Обновляем каждые 5 секунд
        
        # Загружаем логи при открытии
        refresh_logs()
        auto_refresh()
    
    def start_multichat(self):
        """Запускает все включенные каналы мульти-чата"""
        if not self.multichat_enabled_var.get():
            messagebox.showwarning("Предупреждение", "Сначала включите режим мульти-чата")
            return
        
        channels = self.settings.get('multichat_channels', [])
        if not channels:
            messagebox.showwarning("Предупреждение", "Добавьте хотя бы один канал")
            return
        
        # Фильтруем только включенные каналы
        enabled_channels = [ch for ch in channels if ch.get('enabled', False)]
        
        if not enabled_channels:
            messagebox.showwarning("Предупреждение", 
                "Нет включенных каналов!\n\n"
                "Включите хотя бы один канал кнопкой '▶️ Запустить канал' во вкладке 'Мульти-чат'")
            return
        
        # Проверяем, что все включенные каналы имеют корректные URL
        invalid_channels = []
        for channel in enabled_channels:
            if not channel.get('url') or not channel.get('name') or not channel.get('prefix'):
                invalid_channels.append(channel.get('name', 'Неизвестный'))
        
        if invalid_channels:
            messagebox.showwarning("Предупреждение", f"Некорректные каналы: {', '.join(invalid_channels)}")
            return
        
        if self.parser_process and self.parser_process.poll() is None:
            self.log("⚠️ Мульти-чат уже запущен")
            return
        
        try:
            self.log("🚀 Запуск мульти-чата...")
            self.log(f"📊 Включенных каналов для парсинга: {len(enabled_channels)}")
            for ch in enabled_channels:
                self.log(f"  ✓ {ch.get('name')} ({ch.get('prefix')})")
            
            # Запускаем мульти-чат координатор через venv Python
            venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "python.exe")
            
            self.parser_process = subprocess.Popen(
                [venv_python, "multichat_coordinator.py", "--output", "messages.json", "--max-messages", str(self.settings.get('max_messages', 50))],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                env=self.get_clean_env()
            )
            
            self.parser_status_label.config(text="Мульти-чат: Работает", foreground="green")
            self.log("✅ Мульти-чат запущен")
            
            # Мониторим процесс мульти-чата
            threading.Thread(target=self.monitor_multichat, daemon=True).start()
            
        except Exception as e:
            self.log(f"❌ Ошибка запуска мульти-чата: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось запустить мульти-чат:\n{str(e)}")
    
    def stop_multichat(self):
        """Останавливает все каналы мульти-чата"""
        self.log("🛑 Остановка мульти-чата...")
        if self.parser_process:
            try:
                # Сначала пытаемся корректно завершить
                self.parser_process.terminate()
                # Ждем 2 секунды
                try:
                    self.parser_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    # Если процесс не завершился - убиваем принудительно
                    self.log("⚠️ Координатор не отвечает, принудительная остановка...")
                    self.parser_process.kill()
                    self.parser_process.wait()
                
                self.log("✅ Мульти-чат координатор остановлен")
            except Exception as e:
                self.log(f"⚠️ Ошибка при остановке координатора: {e}")
            finally:
                self.parser_process = None
                
            # Дополнительно убиваем ВСЕ процессы парсеров через системную команду
            self.log("🧹 Очистка оставшихся процессов парсеров...")
            try:
                # Убиваем все процессы chat_parser_pytchat.py
                subprocess.run(
                    ['taskkill', '/F', '/FI', 'WINDOWTITLE eq *chat_parser*'],
                    capture_output=True,
                    timeout=5
                )
                self.log("✅ Процессы парсеров очищены")
            except Exception as e:
                self.log(f"⚠️ Ошибка при очистке парсеров: {e}")
                
            self.parser_status_label.config(text="Мульти-чат: Остановлен", foreground="red")
            self.log("🛑 Мульти-чат полностью остановлен")
    
    def start_selected_channel(self):
        """Включает выбранный канал"""
        selected = self.channels_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите канал для включения")
            return
        
        item = self.channels_tree.item(selected[0])
        values = item['values']
        prefix = values[1]  # Префикс теперь на позиции 1 (после статуса)
        name = values[2]
        url = values[3]
        
        # Проверяем наличие URL
        if not url:
            messagebox.showwarning("Предупреждение", f"У канала {name} не указан URL")
            return
        
        # Находим канал в настройках и включаем его
        channels = self.settings.get('multichat_channels', [])
        for channel in channels:
            if channel.get('prefix') == prefix:
                channel['enabled'] = True
                break
        
        self.settings['multichat_channels'] = channels
        self.save_settings()
        self.refresh_channel_status()
        
        self.log(f"✅ Канал {name} ({prefix}) включен")
        self.log(f"💡 Запустите мульти-чат из вкладки 'Управление' для применения изменений")
    
    def stop_selected_channel(self):
        """Останавливает выбранный канал"""
        selected = self.channels_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите канал для остановки")
            return
        
        item = self.channels_tree.item(selected[0])
        values = item['values']
        prefix = values[1]  # Префикс теперь на позиции 1 (после статуса)
        name = values[2]
        
        # Проверяем, запущен ли этот канал
        if prefix not in self.channel_processes:
            self.log(f"⚠️ Канал {name} не запущен")
            return
        
        try:
            self.log(f"🛑 Остановка канала: {name} ({prefix})")
            
            process = self.channel_processes[prefix]
            if process:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            
            del self.channel_processes[prefix]
            self.log(f"✅ Канал {name} остановлен")
            
            # Обновляем отображение статуса
            self.refresh_channel_status()
            
        except Exception as e:
            self.log(f"⚠️ Ошибка при остановке канала {name}: {e}")
    
    def refresh_channel_status(self):
        """Обновляет статусы всех каналов в таблице"""
        # Перезагружаем список каналов чтобы обновить статусы
        self.load_channels()
    
    def monitor_multichat(self):
        """Мониторинг мульти-чата с проверкой статуса"""
        last_status = ""
        
        while self.parser_process and self.parser_process.poll() is None:
            try:
                # Читаем статус из файла (для мульти-чата)
                try:
                    with open('multichat_status.txt', 'r', encoding='utf-8') as f:
                        status = f.read().strip()
                        if status and status != last_status:
                            if status.startswith("ERROR"):
                                self.root.after(0, lambda s=status: self.log(f"❌ {s}"))
                                self.root.after(0, lambda: self.parser_status_label.config(text="Мульти-чат: Ошибка", foreground="red"))
                            elif status == "STARTING":
                                self.root.after(0, lambda: self.log("🔄 Запуск мульти-чата..."))
                                self.root.after(0, lambda: self.parser_status_label.config(text="Мульти-чат: Запуск", foreground="orange"))
                            elif status.startswith("RUNNING"):
                                # Обновляем счетчик каналов
                                if ": " in status:
                                    channel_info = status.split(": ")[1]
                                    self.root.after(0, lambda s=channel_info: self.parser_status_label.config(text=f"Мульти-чат: {s}", foreground="green"))
                                else:
                                    self.root.after(0, lambda: self.parser_status_label.config(text="Мульти-чат: Работает", foreground="green"))
                            elif status == "STOPPING":
                                self.root.after(0, lambda: self.log("🛑 Остановка мульти-чата..."))
                                self.root.after(0, lambda: self.parser_status_label.config(text="Мульти-чат: Остановка", foreground="orange"))
                            elif status == "STOPPED":
                                self.root.after(0, lambda: self.log("✅ Мульти-чат остановлен"))
                                self.root.after(0, lambda: self.parser_status_label.config(text="Мульти-чат: Остановлен", foreground="red"))
                            
                            last_status = status
                except FileNotFoundError:
                    pass
                
                time.sleep(2)  # Проверяем каждые 2 секунды
                
            except Exception as error:
                self.root.after(0, lambda err=error: self.log(f"❌ Ошибка мониторинга мульти-чата: {err}"))
                break
        
        # Процесс завершился
        if self.parser_process:
            return_code = self.parser_process.poll()
            if return_code is not None:
                if return_code != 0:
                    self.root.after(0, lambda: self.log(f"❌ Мульти-чат завершился с ошибкой (код: {return_code})"))
                    self.root.after(0, lambda: self.parser_status_label.config(text="Мульти-чат: Ошибка", foreground="red"))
                else:
                    self.root.after(0, lambda: self.log("✅ Мульти-чат завершен"))
                    self.root.after(0, lambda: self.parser_status_label.config(text="Мульти-чат: Остановлен", foreground="red"))
        
    def on_closing(self):
        """Обработчик закрытия приложения"""
        logging.warning("!!! on_closing() ВЫЗВАН! Окно закрывается!")
        logging.info("Остановка всех процессов перед закрытием...")
        self.stop_all()
        logging.info("Уничтожение окна root.destroy()...")
        self.root.destroy()
        logging.info("Окно уничтожено.")

if __name__ == "__main__":
    setup_logging()
    logging.info("Запуск приложения...")
    
    try:
        root = tk.Tk()
        
        app = YouTubeChatGUISimple(root)
        
        logging.info("Установка protocol WM_DELETE_WINDOW...")
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        logging.info("Protocol установлен.")
        
        logging.info("Запуск главного цикла tkinter (mainloop)...")
        root.mainloop()
        logging.info("Приложение закрыто (mainloop завершен).")
    except Exception as e:
        logging.error(f"КРИТИЧЕСКАЯ ОШИБКА в main: {e}", exc_info=True)
        input("Нажмите Enter...") 