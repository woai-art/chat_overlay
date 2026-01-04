#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Минимальный тест GUI - проверка работы tkinter"""

import tkinter as tk
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_minimal_gui.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logging.info("=== СТАРТ ТЕСТА МИНИМАЛЬНОГО GUI ===")

try:
    logging.info("Создание корневого окна tk.Tk()...")
    root = tk.Tk()
    logging.info("Корневое окно создано успешно.")
    
    logging.info("Установка заголовка...")
    root.title("Минимальный тест GUI")
    logging.info("Заголовок установлен.")
    
    logging.info("Установка размера окна...")
    root.geometry("400x300")
    logging.info("Размер установлен.")
    
    logging.info("Создание метки (Label)...")
    label = tk.Label(root, text="Если вы видите это окно, tkinter работает правильно!", 
                     font=("Arial", 14), pady=20)
    label.pack()
    logging.info("Метка создана и размещена.")
    
    logging.info("Создание кнопки...")
    button = tk.Button(root, text="Закрыть", command=root.destroy, font=("Arial", 12))
    button.pack()
    logging.info("Кнопка создана и размещена.")
    
    logging.info("Запуск mainloop()...")
    root.mainloop()
    logging.info("mainloop() завершен. Окно закрыто пользователем.")
    
except Exception as e:
    logging.error(f"КРИТИЧЕСКАЯ ОШИБКА: {e}", exc_info=True)
    input("Нажмите Enter для выхода...")

logging.info("=== КОНЕЦ ТЕСТА ===")

