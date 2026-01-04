#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Генератор полной базы данных эмоджи
Объединяет Unicode эмоджи и YouTube эмоджи в оптимизированную структуру
"""

import json
import csv
import os
import requests
from pathlib import Path
from typing import Dict, List, Tuple
import time

class EmojiDatabaseGenerator:
    """Генератор базы данных эмоджи"""
    
    def __init__(self):
        self.unicode_path = Path("D:/vMix/liveChat/Emoji-List-Unicode")
        self.youtube_csv_path = Path("D:/vMix/liveChat/youtubeemoji.csv")
        self.output_dir = Path(".")
        
        # Результирующие базы данных
        self.popular_emojis = {}
        self.basic_emojis = {}
        self.full_emojis = {}
        self.youtube_emojis = {}
        
        # Статистика
        self.stats = {
            'unicode_processed': 0,
            'youtube_processed': 0,
            'duplicates_removed': 0,
            'categories': set()
        }
    
    def load_unicode_emojis(self):
        """Загружает Unicode эмоджи из JSON файлов"""
        print("Загрузка Unicode эмоджи...")
        
        # Загружаем основные эмоджи
        all_emoji_path = self.unicode_path / "json" / "all-emoji.json"
        if all_emoji_path.exists():
            with open(all_emoji_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            current_category = ""
            for item in data:
                if len(item) == 1:  # Категория
                    current_category = item[0]
                    self.stats['categories'].add(current_category)
                elif len(item) == 4 and item[0].isdigit():  # Эмоджи
                    unicode_code, emoji, description = item[1], item[2], item[3]
                    
                    # Создаем код эмоджи
                    code = self._create_emoji_code(description)
                    
                    # Определяем уровень популярности
                    if self._is_popular_emoji(description, emoji):
                        self.popular_emojis[code] = emoji
                    elif "U+1F3F" not in unicode_code:  # Без модификаторов тона кожи
                        self.basic_emojis[code] = emoji
                    else:  # С модификаторами
                        self.full_emojis[code] = emoji
                    
                    self.stats['unicode_processed'] += 1
        
        # Загружаем эмоджи с модификаторами
        modifiers_path = self.unicode_path / "json" / "full-emoji-modifiers.json"
        if modifiers_path.exists():
            with open(modifiers_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item in data:
                if len(item) == 4 and item[0].isdigit():
                    unicode_code, emoji, description = item[1], item[2], item[3]
                    code = self._create_emoji_code(description)
                    
                    # Все модификаторы идут в полную базу
                    if code not in self.popular_emojis and code not in self.basic_emojis:
                        self.full_emojis[code] = emoji
                        self.stats['unicode_processed'] += 1
        
        print(f"Загружено {self.stats['unicode_processed']} Unicode эмоджи")
        print(f"   Популярные: {len(self.popular_emojis)}")
        print(f"   Базовые: {len(self.basic_emojis)}")
        print(f"   Полные: {len(self.full_emojis)}")
    
    def load_youtube_emojis(self):
        """Загружает YouTube эмоджи из CSV файла"""
        print("Загрузка YouTube эмоджи...")
        
        if not self.youtube_csv_path.exists():
            print(f"Файл {self.youtube_csv_path} не найден")
            return
        
        try:
            with open(self.youtube_csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Пропускаем заголовок
                
                for row in reader:
                    if len(row) >= 2:
                        label = row[0].strip('"')
                        url = row[1].strip('"')
                        
                        # Создаем HTML для YouTube эмоджи
                        emoji_html = f'<img src="{url}" alt="{label}" class="youtube-emoji" style="width:24px;height:24px;vertical-align:middle;">'
                        self.youtube_emojis[label] = emoji_html
                        self.stats['youtube_processed'] += 1
            
            print(f"Загружено {self.stats['youtube_processed']} YouTube эмоджи")
            
        except Exception as e:
            print(f"Ошибка загрузки YouTube эмоджи: {e}")
    
    def _create_emoji_code(self, description: str) -> str:
        """Создает код эмоджи из описания"""
        # Очищаем и нормализуем описание
        code = description.lower()
        code = code.replace(' ', '_')
        code = code.replace('-', '_')
        code = code.replace(':', '')
        code = code.replace('(', '')
        code = code.replace(')', '')
        code = code.replace(',', '')
        code = code.replace('.', '')
        code = code.replace('!', '')
        code = code.replace('?', '')
        
        # Убираем множественные подчеркивания
        while '__' in code:
            code = code.replace('__', '_')
        
        # Убираем подчеркивания в начале и конце
        code = code.strip('_')
        
        return f":{code}:"
    
    def _is_popular_emoji(self, description: str, emoji: str) -> bool:
        """Определяет, является ли эмоджи популярным"""
        popular_keywords = [
            'face', 'smile', 'grin', 'laugh', 'cry', 'heart', 'love',
            'thumb', 'hand', 'fire', 'star', 'crown', 'trophy', 'rocket',
            'party', 'birthday', 'gift', 'music', 'clap', 'wave', 'ok',
            'victory', 'peace', 'muscle', 'pray', 'angry', 'sad', 'happy',
            'wink', 'kiss', 'hug', 'think', 'sleep', 'sick', 'hot', 'cold'
        ]
        
        # Популярные Unicode символы
        popular_emojis = [
            '😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃',
            '😉', '😊', '😇', '🥰', '😍', '🤩', '😘', '😗', '☺️', '🤔',
            '😐', '😑', '😶', '😏', '😒', '🙄', '😬', '😌', '😔', '😪',
            '😴', '😷', '🥵', '🥶', '🥴', '😵', '🤯', '🤠', '🥳', '😎',
            '🤓', '😕', '😟', '🙁', '☹️', '😮', '😯', '😲', '😳', '🥺',
            '😢', '😭', '😱', '😠', '😡', '💀', '👍', '👎', '👌', '✌️',
            '🤞', '✋', '👋', '🤙', '💪', '👏', '🙌', '🙏', '❤️', '🧡',
            '💛', '💚', '💙', '💜', '🖤', '🤍', '💔', '🔥', '💯', '💥',
            '⭐', '🌟', '💎', '👑', '🏆', '🚀', '💰', '🎁', '🎂', '🎉',
            '🎊', '🎈', '🎵', '🎶'
        ]
        
        desc_lower = description.lower()
        
        # Проверяем по ключевым словам
        for keyword in popular_keywords:
            if keyword in desc_lower:
                return True
        
        # Проверяем по Unicode символу
        if emoji in popular_emojis:
            return True
        
        return False
    
    def remove_duplicates(self):
        """Удаляет дубликаты между уровнями"""
        print("Удаление дубликатов...")
        
        # Удаляем из basic_emojis то, что есть в popular_emojis
        for code in list(self.basic_emojis.keys()):
            if code in self.popular_emojis:
                del self.basic_emojis[code]
                self.stats['duplicates_removed'] += 1
        
        # Удаляем из full_emojis то, что есть в popular_emojis или basic_emojis
        for code in list(self.full_emojis.keys()):
            if code in self.popular_emojis or code in self.basic_emojis:
                del self.full_emojis[code]
                self.stats['duplicates_removed'] += 1
        
        print(f"Удалено {self.stats['duplicates_removed']} дубликатов")
    
    def add_custom_mappings(self):
        """Добавляет кастомные маппинги для популярных сокращений"""
        print("Добавление кастомных маппингов...")
        
        custom_mappings = {
            # ASCII эмотиконы
            ':)': '😊',
            ':-)': '😊',
            ':(': '😢',
            ':-(': '😢',
            ':D': '😄',
            ':-D': '😄',
            ':P': '😛',
            ':-P': '😛',
            ';)': '😉',
            ';-)': '😉',
            ':o': '😮',
            ':-o': '😮',
            ':O': '😱',
            ':-O': '😱',
            ':|': '😐',
            ':-|': '😐',
            ':*': '😘',
            ':-*': '😘',
            '<3': '❤️',
            '</3': '💔',
            
            # Популярные сокращения
            ':heart:': '❤️',
            ':thumbsup:': '👍',
            ':thumbsdown:': '👎',
            ':clap:': '👏',
            ':wave:': '👋',
            ':eyes:': '👀',
            ':100:': '💯',
            
            # Twitch/YouTube сленг
            ':pogchamp:': '😲',
            ':kappa:': '😏',
            ':pepehands:': '😢',
            ':pepega:': '🤪',
            ':5head:': '🧠',
            ':monkas:': '😰',
            ':omegalul:': '😂',
            ':lul:': '😂',
            ':ez:': '😎',
            ':sadge:': '😢',
            ':copium:': '🤡',
            ':hopium:': '🙏',
            ':gigachad:': '💪',
            ':based:': '😎',
            ':cringe:': '😬',
            ':sus:': '🤔',
            ':no_cap:': '💯',
            ':fr:': '💯',
            ':bussin:': '🔥',
            ':sheesh:': '😤',
            ':W:': '🏆',
            ':L:': '💀',
            ':ratio:': '📈',
            ':cap:': '🧢',
            ':facts:': '💯',
            ':periodt:': '💅',
            ':slay:': '💅',
            ':queen:': '👑',
            ':king:': '👑',
            ':goat:': '🐐',
            ':mood:': '😌',
            ':vibe:': '✨',
            ':energy:': '⚡',
            ':flex:': '💪',
            ':lit:': '🔥',
            ':bet:': '💯',
            ':dead:': '💀',
            ':crying:': '😭',
            ':help:': '😭',
            ':screaming:': '😱'
        }
        
        # Добавляем в популярные эмоджи
        for code, emoji in custom_mappings.items():
            if code not in self.popular_emojis:
                self.popular_emojis[code] = emoji
        
        print(f"Добавлено {len(custom_mappings)} кастомных маппингов")
    
    def generate_python_file(self):
        """Генерирует Python файл с базой данных"""
        print("Генерация Python файла...")
        
        output_path = self.output_dir / "emoji_database_generated.py"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('#!/usr/bin/env python3\n')
            f.write('# -*- coding: utf-8 -*-\n\n')
            f.write('"""\n')
            f.write('Автоматически сгенерированная база данных эмоджи\n')
            f.write(f'Содержит {len(self.popular_emojis) + len(self.basic_emojis) + len(self.full_emojis) + len(self.youtube_emojis)} эмоджи\n')
            f.write('"""\n\n')
            
            # Популярные эмоджи
            f.write('# Популярные эмоджи (Уровень 1) - быстрая загрузка\n')
            f.write('POPULAR_EMOJIS = {\n')
            for code, emoji in sorted(self.popular_emojis.items()):
                f.write(f'    {repr(code)}: {repr(emoji)},\n')
            f.write('}\n\n')
            
            # Базовые эмоджи
            f.write('# Базовые Unicode эмоджи (Уровень 2)\n')
            f.write('BASIC_EMOJIS = {\n')
            for code, emoji in sorted(self.basic_emojis.items()):
                f.write(f'    {repr(code)}: {repr(emoji)},\n')
            f.write('}\n\n')
            
            # Полные эмоджи
            f.write('# Полные Unicode эмоджи с модификаторами (Уровень 3)\n')
            f.write('FULL_EMOJIS = {\n')
            for code, emoji in sorted(self.full_emojis.items()):
                f.write(f'    {repr(code)}: {repr(emoji)},\n')
            f.write('}\n\n')
            
            # YouTube эмоджи
            f.write('# YouTube специфичные эмоджи (Уровень 4)\n')
            f.write('YOUTUBE_EMOJIS = {\n')
            for code, emoji_html in sorted(self.youtube_emojis.items()):
                f.write(f'    {repr(code)}: {repr(emoji_html)},\n')
            f.write('}\n\n')
            
            # Функции
            f.write('''def get_emoji_database(level=2):
    """
    Возвращает базу данных эмоджи для указанного уровня
    
    Args:
        level (int): Уровень базы данных
            1 - только популярные эмоджи
            2 - популярные + базовые
            3 - популярные + базовые + полные
            4 - все эмоджи включая YouTube
    
    Returns:
        dict: База данных эмоджи
    """
    result = POPULAR_EMOJIS.copy()
    
    if level >= 2:
        result.update(BASIC_EMOJIS)
    
    if level >= 3:
        result.update(FULL_EMOJIS)
    
    if level >= 4:
        result.update(YOUTUBE_EMOJIS)
    
    return result

def convert_emojis(text, level=2):
    """
    Конвертирует эмоджи в тексте
    
    Args:
        text (str): Исходный текст
        level (int): Уровень базы данных
    
    Returns:
        str: Текст с замененными эмоджи
    """
    if not text:
        return text
    
    emoji_db = get_emoji_database(level)
    result = text
    
    for code, emoji in emoji_db.items():
        result = result.replace(code, emoji)
    
    return result

def get_stats():
    """Возвращает статистику базы данных"""
    return {
        'popular_count': len(POPULAR_EMOJIS),
        'basic_count': len(BASIC_EMOJIS),
        'full_count': len(FULL_EMOJIS),
        'youtube_count': len(YOUTUBE_EMOJIS),
        'total_count': len(POPULAR_EMOJIS) + len(BASIC_EMOJIS) + len(FULL_EMOJIS) + len(YOUTUBE_EMOJIS)
    }

if __name__ == "__main__":
    print("📊 Статистика базы данных эмоджи:")
    stats = get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Тест конвертации
    test_text = "Привет :fire: :heart: :thumbsup: :grinning_face: :rocket:"
    print(f"\\n🧪 Тест конвертации:")
    print(f"   Исходный текст: {test_text}")
    print(f"   Результат: {convert_emojis(test_text)}")
''')
        
        print(f"Python файл сохранен: {output_path}")
    
    def generate_javascript_file(self):
        """Генерирует JavaScript файл с базой данных"""
        print("Генерация JavaScript файла...")
        
        output_path = self.output_dir / "emoji_database_generated.js"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('// =============================================================================\n')
            f.write('// АВТОМАТИЧЕСКИ СГЕНЕРИРОВАННАЯ БАЗА ДАННЫХ ЭМОДЖИ\n')
            f.write(f'// Содержит {len(self.popular_emojis) + len(self.basic_emojis) + len(self.full_emojis) + len(self.youtube_emojis)} эмоджи\n')
            f.write('// =============================================================================\n\n')
            
            # Популярные эмоджи
            f.write('// Популярные эмоджи (Уровень 1) - быстрая загрузка\n')
            f.write('const POPULAR_EMOJIS = {\n')
            for code, emoji in sorted(self.popular_emojis.items()):
                f.write(f'    {json.dumps(code)}: {json.dumps(emoji)},\n')
            f.write('};\n\n')
            
            # Базовые эмоджи
            f.write('// Базовые Unicode эмоджи (Уровень 2)\n')
            f.write('const BASIC_EMOJIS = {\n')
            for code, emoji in sorted(self.basic_emojis.items()):
                f.write(f'    {json.dumps(code)}: {json.dumps(emoji)},\n')
            f.write('};\n\n')
            
            # Полные эмоджи (только первые 1000 для производительности)
            f.write('// Полные Unicode эмоджи с модификаторами (Уровень 3) - ограничено для производительности\n')
            f.write('const FULL_EMOJIS = {\n')
            limited_full = dict(list(sorted(self.full_emojis.items()))[:1000])
            for code, emoji in limited_full.items():
                f.write(f'    {json.dumps(code)}: {json.dumps(emoji)},\n')
            f.write('};\n\n')
            
            # YouTube эмоджи
            f.write('// YouTube специфичные эмоджи (Уровень 4)\n')
            f.write('const YOUTUBE_EMOJIS = {\n')
            for code, emoji_html in sorted(self.youtube_emojis.items()):
                f.write(f'    {json.dumps(code)}: {json.dumps(emoji_html)},\n')
            f.write('};\n\n')
            
            # Функции
            f.write('''function getEmojiDatabase(level = 2) {
    /**
     * Возвращает базу данных эмоджи для указанного уровня
     * 
     * @param {number} level - Уровень базы данных (1-4)
     * @returns {Object} База данных эмоджи
     */
    const result = {...POPULAR_EMOJIS};
    
    if (level >= 2) {
        Object.assign(result, BASIC_EMOJIS);
    }
    
    if (level >= 3) {
        Object.assign(result, FULL_EMOJIS);
    }
    
    if (level >= 4) {
        Object.assign(result, YOUTUBE_EMOJIS);
    }
    
    return result;
}

function convertEmojis(text, level = 2) {
    /**
     * Конвертирует эмоджи в тексте
     * 
     * @param {string} text - Исходный текст
     * @param {number} level - Уровень базы данных
     * @returns {string} Текст с замененными эмоджи
     */
    if (!text) return text;
    
    const emojiDB = getEmojiDatabase(level);
    let result = text;
    
    for (const [code, emoji] of Object.entries(emojiDB)) {
        const escapedCode = code.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
        result = result.replace(new RegExp(escapedCode, 'g'), emoji);
    }
    
    return result;
}

function getEmojiStats() {
    /**
     * Возвращает статистику базы данных
     * @returns {Object} Статистика
     */
    return {
        popularCount: Object.keys(POPULAR_EMOJIS).length,
        basicCount: Object.keys(BASIC_EMOJIS).length,
        fullCount: Object.keys(FULL_EMOJIS).length,
        youtubeCount: Object.keys(YOUTUBE_EMOJIS).length,
        totalCount: Object.keys(POPULAR_EMOJIS).length + 
                   Object.keys(BASIC_EMOJIS).length + 
                   Object.keys(FULL_EMOJIS).length + 
                   Object.keys(YOUTUBE_EMOJIS).length
    };
}

// Экспорт для Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        POPULAR_EMOJIS,
        BASIC_EMOJIS,
        FULL_EMOJIS,
        YOUTUBE_EMOJIS,
        getEmojiDatabase,
        convertEmojis,
        getEmojiStats
    };
}

// Глобальные переменные для браузера
if (typeof window !== 'undefined') {
    window.POPULAR_EMOJIS = POPULAR_EMOJIS;
    window.BASIC_EMOJIS = BASIC_EMOJIS;
    window.FULL_EMOJIS = FULL_EMOJIS;
    window.YOUTUBE_EMOJIS = YOUTUBE_EMOJIS;
    window.getEmojiDatabase = getEmojiDatabase;
    window.convertEmojis = convertEmojis;
    window.getEmojiStats = getEmojiStats;
}

// Автоматическое тестирование
console.log('📊 Статистика базы данных эмоджи:');
const stats = getEmojiStats();
for (const [key, value] of Object.entries(stats)) {
    console.log(`   ${key}: ${value}`);
}

// Тест конвертации
const testText = "Привет :fire: :heart: :thumbsup: :grinning_face: :rocket:";
console.log('\\n🧪 Тест конвертации:');
console.log(`   Исходный текст: ${testText}`);
console.log(`   Результат: ${convertEmojis(testText)}`);
''')
        
        print(f"JavaScript файл сохранен: {output_path}")
    
    def generate_json_files(self):
        """Генерирует JSON файлы для каждого уровня"""
        print("Генерация JSON файлов...")
        
        # Популярные эмоджи
        with open(self.output_dir / "popular_emojis.json", 'w', encoding='utf-8') as f:
            json.dump(self.popular_emojis, f, ensure_ascii=False, indent=2)
        
        # Базовые эмоджи
        with open(self.output_dir / "basic_emojis.json", 'w', encoding='utf-8') as f:
            json.dump(self.basic_emojis, f, ensure_ascii=False, indent=2)
        
        # Полные эмоджи (разбиваем на части для производительности)
        chunk_size = 1000
        full_items = list(self.full_emojis.items())
        for i in range(0, len(full_items), chunk_size):
            chunk = dict(full_items[i:i + chunk_size])
            chunk_num = i // chunk_size + 1
            with open(self.output_dir / f"full_emojis_part{chunk_num}.json", 'w', encoding='utf-8') as f:
                json.dump(chunk, f, ensure_ascii=False, indent=2)
        
        # YouTube эмоджи
        with open(self.output_dir / "youtube_emojis.json", 'w', encoding='utf-8') as f:
            json.dump(self.youtube_emojis, f, ensure_ascii=False, indent=2)
        
        print("JSON файлы сохранены")
    
    def print_stats(self):
        """Выводит финальную статистику"""
        print("\n" + "="*60)
        print("ФИНАЛЬНАЯ СТАТИСТИКА ГЕНЕРАЦИИ")
        print("="*60)
        print(f"Unicode эмоджи обработано: {self.stats['unicode_processed']}")
        print(f"YouTube эмоджи обработано: {self.stats['youtube_processed']}")
        print(f"Дубликатов удалено: {self.stats['duplicates_removed']}")
        print(f"Категорий найдено: {len(self.stats['categories'])}")
        print()
        print("Распределение по уровням:")
        print(f"  Уровень 1 (Популярные): {len(self.popular_emojis)}")
        print(f"  Уровень 2 (Базовые): {len(self.basic_emojis)}")
        print(f"  Уровень 3 (Полные): {len(self.full_emojis)}")
        print(f"  Уровень 4 (YouTube): {len(self.youtube_emojis)}")
        print(f"  ВСЕГО: {len(self.popular_emojis) + len(self.basic_emojis) + len(self.full_emojis) + len(self.youtube_emojis)}")
        print()
        print("Категории Unicode эмоджи:")
        for category in sorted(self.stats['categories']):
            print(f"  - {category}")
    
    def generate_all(self):
        """Генерирует полную базу данных эмоджи"""
        print("Начинаем генерацию базы данных эмоджи")
        print("="*60)
        
        start_time = time.time()
        
        # Загружаем данные
        self.load_unicode_emojis()
        self.load_youtube_emojis()
        
        # Обрабатываем данные
        self.add_custom_mappings()
        self.remove_duplicates()
        
        # Генерируем файлы
        self.generate_python_file()
        self.generate_javascript_file()
        self.generate_json_files()
        
        # Статистика
        self.print_stats()
        
        end_time = time.time()
        print(f"\nГенерация завершена за {end_time - start_time:.2f} секунд")
        print("Все файлы успешно созданы!")

if __name__ == "__main__":
    generator = EmojiDatabaseGenerator()
    generator.generate_all()
