#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Улучшенная база данных эмоджи для YouTube Live Chat Parser
Многоуровневая система с оптимизацией производительности
"""

import json
import re
import time
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path

# Импортируем утилиты для работы с консолью
try:
    from console_utils import setup_console_encoding, print_with_fallback
    # Настраиваем кодировку при импорте
    setup_console_encoding()
    safe_print = print_with_fallback
except ImportError:
    # Fallback если console_utils недоступен
    safe_print = print

class EmojiDatabase:
    """
    Оптимизированная база данных эмоджи с многоуровневой системой приоритетов
    """
    
    def __init__(self):
        self.popular_emojis = {}  # Уровень 1: Популярные эмоджи
        self.basic_emojis = {}    # Уровень 2: Базовые Unicode
        self.full_emojis = {}     # Уровень 3: Полная база
        self.youtube_emojis = {}  # Уровень 4: YouTube эмоджи
        self.honey_club_emojis = {}  # Уровень 5: Персональные эмоджи канала
        
        # Кэш для производительности
        self.emoji_cache = {}
        self.compiled_patterns = {}
        
        # Статистика использования
        self.usage_stats = {}
        
        # Флаги загрузки
        self.levels_loaded = {1: False, 2: False, 3: False, 4: False, 5: False}
        
        # Загружаем популярные эмоджи при инициализации
        self._load_popular_emojis()
    
    def _load_popular_emojis(self):
        """Загрузка популярных эмоджи (Уровень 1)"""
        self.popular_emojis = {
            # Лица и эмоции (самые популярные)
            ':grinning_face:': '😀',
            ':grinning_face_with_big_eyes:': '😃',
            ':grinning_face_with_smiling_eyes:': '😄',
            ':beaming_face_with_smiling_eyes:': '😁',
            ':grinning_squinting_face:': '😆',
            ':grinning_face_with_sweat:': '😅',
            ':rolling_on_the_floor_laughing:': '🤣',
            ':face_with_tears_of_joy:': '😂',
            ':slightly_smiling_face:': '🙂',
            ':upside_down_face:': '🙃',
            ':winking_face:': '😉',
            ':smiling_face_with_smiling_eyes:': '😊',
            ':smiling_face_with_halo:': '😇',
            ':smiling_face_with_hearts:': '🥰',
            ':smiling_face_with_heart_eyes:': '😍',
            ':star_struck:': '🤩',
            ':face_blowing_a_kiss:': '😘',
            ':kissing_face:': '😗',
            ':smiling_face:': '☺️',
            ':thinking_face:': '🤔',
            ':neutral_face:': '😐',
            ':expressionless_face:': '😑',
            ':face_without_mouth:': '😶',
            ':smirking_face:': '😏',
            ':unamused_face:': '😒',
            ':face_with_rolling_eyes:': '🙄',
            ':grimacing_face:': '😬',
            ':relieved_face:': '😌',
            ':pensive_face:': '😔',
            ':sleepy_face:': '😪',
            ':sleeping_face:': '😴',
            ':face_with_medical_mask:': '😷',
            ':hot_face:': '🥵',
            ':cold_face:': '🥶',
            ':woozy_face:': '🥴',
            ':dizzy_face:': '😵',
            ':exploding_head:': '🤯',
            ':cowboy_hat_face:': '🤠',
            ':partying_face:': '🥳',
            ':smiling_face_with_sunglasses:': '😎',
            ':nerd_face:': '🤓',
            ':confused_face:': '😕',
            ':worried_face:': '😟',
            ':slightly_frowning_face:': '🙁',
            ':frowning_face:': '☹️',
            ':face_with_open_mouth:': '😮',
            ':hushed_face:': '😯',
            ':astonished_face:': '😲',
            ':flushed_face:': '😳',
            ':pleading_face:': '🥺',
            ':crying_face:': '😢',
            ':loudly_crying_face:': '😭',
            ':face_screaming_in_fear:': '😱',
            ':angry_face:': '😠',
            ':pouting_face:': '😡',
            ':skull:': '💀',
            
            # Жесты и руки
            ':thumbs_up:': '👍',
            ':thumbs_down:': '👎',
            ':ok_hand:': '👌',
            ':victory_hand:': '✌️',
            ':crossed_fingers:': '🤞',
            ':raised_hand:': '✋',
            ':waving_hand:': '👋',
            ':call_me_hand:': '🤙',
            ':flexed_biceps:': '💪',
            ':clapping_hands:': '👏',
            ':raising_hands:': '🙌',
            ':folded_hands:': '🙏',
            
            # Сердца
            ':red_heart:': '❤️',
            ':orange_heart:': '🧡',
            ':yellow_heart:': '💛',
            ':green_heart:': '💚',
            ':blue_heart:': '💙',
            ':purple_heart:': '💜',
            ':black_heart:': '🖤',
            ':white_heart:': '🤍',
            ':broken_heart:': '💔',
            
            # Популярные символы
            ':fire:': '🔥',
            ':hundred_points:': '💯',
            ':collision:': '💥',
            ':star:': '⭐',
            ':glowing_star:': '🌟',
            ':gem:': '💎',
            ':crown:': '👑',
            ':trophy:': '🏆',
            ':rocket:': '🚀',
            ':money_bag:': '💰',
            ':gift:': '🎁',
            ':birthday_cake:': '🎂',
            ':party_popper:': '🎉',
            ':confetti_ball:': '🎊',
            ':balloon:': '🎈',
            ':musical_note:': '🎵',
            ':musical_notes:': '🎶',
            
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
            
            # Популярные Twitch/YouTube эмоджи
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
        
        self.levels_loaded[1] = True
        self._compile_patterns(self.popular_emojis)
    
    def _load_basic_emojis(self):
        """Загрузка базовых Unicode эмоджи (Уровень 2)"""
        if self.levels_loaded[2]:
            return
            
        try:
            unicode_path = Path("D:/vMix/liveChat/Emoji-List-Unicode/json/all-emoji.json")
            if unicode_path.exists():
                with open(unicode_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Парсим JSON и создаем базовые эмоджи (без модификаторов)
                current_category = ""
                for item in data:
                    if len(item) == 1:  # Категория
                        current_category = item[0]
                    elif len(item) == 4 and item[0].isdigit():  # Эмоджи
                        unicode_code, emoji, description = item[1], item[2], item[3]
                        # Пропускаем эмоджи с модификаторами тона кожи
                        if "U+1F3F" not in unicode_code:
                            code = f":{description.lower().replace(' ', '_').replace('-', '_')}:"
                            if code not in self.popular_emojis:  # Не дублируем популярные
                                self.basic_emojis[code] = emoji
                
                self.levels_loaded[2] = True
                safe_print(f"Загружено {len(self.basic_emojis)} базовых эмоджи")
                
        except Exception as e:
            print(f"Ошибка загрузки базовых эмоджи: {e}")
    
    def _load_full_emojis(self):
        """Загрузка полной базы эмоджи с модификаторами (Уровень 3)"""
        if self.levels_loaded[3]:
            return
            
        try:
            # Загружаем базовые эмоджи если еще не загружены
            self._load_basic_emojis()
            
            # Загружаем эмоджи с модификаторами
            modifiers_path = Path("D:/vMix/liveChat/Emoji-List-Unicode/json/full-emoji-modifiers.json")
            if modifiers_path.exists():
                with open(modifiers_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for item in data:
                    if len(item) == 4 and item[0].isdigit():
                        unicode_code, emoji, description = item[1], item[2], item[3]
                        code = f":{description.lower().replace(' ', '_').replace('-', '_')}:"
                        if code not in self.popular_emojis and code not in self.basic_emojis:
                            self.full_emojis[code] = emoji
                
                self.levels_loaded[3] = True
                safe_print(f"Загружено {len(self.full_emojis)} эмоджи с модификаторами")
                
        except Exception as e:
            print(f"Ошибка загрузки полной базы эмоджи: {e}")
    
    def _load_youtube_emojis(self):
        """Загрузка YouTube специфичных эмоджи (Уровень 4)"""
        if self.levels_loaded[4]:
            return
            
        try:
            # Сначала пробуем загрузить из обновленного JSON с локальными путями
            youtube_json_path = Path("youtube_emojis.json")
            if youtube_json_path.exists():
                with open(youtube_json_path, 'r', encoding='utf-8') as f:
                    youtube_data = json.load(f)
                    # JSON уже содержит готовые HTML-теги с локальными путями
                    self.youtube_emojis.update(youtube_data)
                    self.levels_loaded[4] = True
                    safe_print(f"Загружено {len(self.youtube_emojis)} YouTube эмоджи из JSON (локальные пути)")
                    return
            
            # Fallback: загружаем из CSV (старый способ)
            youtube_path = Path("D:/vMix/liveChat/youtubeemoji.csv")
            if youtube_path.exists():
                with open(youtube_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[1:]  # Пропускаем заголовок
                    
                for line in lines:
                    if '","' in line:
                        parts = line.strip().split('","')
                        if len(parts) >= 2:
                            label = parts[0].strip('"')
                            url = parts[1].strip('"')
                            # Для YouTube эмоджи сохраняем URL изображения
                            self.youtube_emojis[label] = f'<img src="{url}" alt="{label}" class="youtube-emoji">'
                
                self.levels_loaded[4] = True
                safe_print(f"Загружено {len(self.youtube_emojis)} YouTube эмоджи из CSV")
                
        except Exception as e:
            print(f"Ошибка загрузки YouTube эмоджи: {e}")
    
    def _load_honey_club_emojis(self):
        """Загрузка персональных эмоджи канала Honey Club (Уровень 5)"""
        if self.levels_loaded[5]:
            return
            
        try:
            # Импортируем модуль персональных эмоджи
            from honey_club_emojis import get_honey_club_emojis
            
            self.honey_club_emojis = get_honey_club_emojis()
            self.levels_loaded[5] = True
            safe_print(f"🍯 Загружено {len(self.honey_club_emojis)} персональных эмоджи канала Honey Club")
            
        except ImportError:
            safe_print("⚠️ Модуль персональных эмоджи не найден")
        except Exception as e:
            print(f"Ошибка загрузки персональных эмоджи: {e}")
    
    def _compile_patterns(self, emoji_dict: Dict[str, str]):
        """Предварительная компиляция регулярных выражений для быстрой замены"""
        for code in emoji_dict.keys():
            if code not in self.compiled_patterns:
                # Экранируем специальные символы
                escaped_code = re.escape(code)
                self.compiled_patterns[code] = re.compile(escaped_code)
    
    def convert_emojis(self, text: str, max_level: int = 2) -> str:
        """
        Конвертирует текстовые коды эмоджи в Unicode символы
        
        Args:
            text (str): Исходный текст с кодами эмоджи
            max_level (int): Максимальный уровень поиска (1-5)
                1 - только популярные эмоджи (быстро)
                2 - популярные + базовые Unicode (умеренно)
                3 - популярные + базовые + полные (медленно)
                4 - все включая YouTube эмоджи (очень медленно)
                5 - все включая персональные эмоджи канала (максимум)
        
        Returns:
            str: Текст с замененными эмоджи
        """
        if not text:
            return text
        
        start_time = time.time()
        result = text
        replacements_made = 0
        
        # Уровень 1: Популярные эмоджи (всегда загружены)
        for code, emoji in self.popular_emojis.items():
            if code in result:
                result = result.replace(code, emoji)
                replacements_made += 1
                self._update_usage_stats(code)
        
        # Уровень 2: Базовые эмоджи
        if max_level >= 2:
            self._load_basic_emojis()
            for code, emoji in self.basic_emojis.items():
                if code in result:
                    result = result.replace(code, emoji)
                    replacements_made += 1
                    self._update_usage_stats(code)
        
        # Уровень 3: Полные эмоджи
        if max_level >= 3:
            self._load_full_emojis()
            for code, emoji in self.full_emojis.items():
                if code in result:
                    result = result.replace(code, emoji)
                    replacements_made += 1
                    self._update_usage_stats(code)
        
        # Уровень 4: YouTube эмоджи
        if max_level >= 4:
            self._load_youtube_emojis()
            for code, emoji_html in self.youtube_emojis.items():
                if code in result:
                    result = result.replace(code, emoji_html)
                    replacements_made += 1
                    self._update_usage_stats(code)
        
        # Уровень 5: Персональные эмоджи канала Honey Club
        if max_level >= 5:
            self._load_honey_club_emojis()
            for code, emoji_html in self.honey_club_emojis.items():
                if code in result:
                    result = result.replace(code, emoji_html)
                    replacements_made += 1
                    self._update_usage_stats(code)
        
        processing_time = time.time() - start_time
        
        # Логируем производительность если обработка заняла много времени
        if processing_time > 0.01:  # Больше 10ms
            safe_print(f"⚠️ Медленная обработка эмоджи: {processing_time:.3f}s, замен: {replacements_made}, уровень: {max_level}")
        
        return result
    
    def _update_usage_stats(self, code: str):
        """Обновляет статистику использования эмоджи"""
        self.usage_stats[code] = self.usage_stats.get(code, 0) + 1
    
    def get_popular_emojis_by_usage(self, limit: int = 50) -> Dict[str, int]:
        """Возвращает самые используемые эмоджи"""
        return dict(sorted(self.usage_stats.items(), key=lambda x: x[1], reverse=True)[:limit])
    
    def optimize_popular_emojis(self):
        """Оптимизирует список популярных эмоджи на основе статистики использования"""
        if len(self.usage_stats) < 100:  # Недостаточно данных для оптимизации
            return
        
        # Находим часто используемые эмоджи из других уровней
        popular_from_usage = self.get_popular_emojis_by_usage(100)
        
        for code, usage_count in popular_from_usage.items():
            if usage_count > 10 and code not in self.popular_emojis:
                # Перемещаем часто используемые эмоджи в популярные
                if code in self.basic_emojis:
                    self.popular_emojis[code] = self.basic_emojis[code]
                    del self.basic_emojis[code]
                elif code in self.full_emojis:
                    self.popular_emojis[code] = self.full_emojis[code]
                    del self.full_emojis[code]
        
        safe_print(f"🔧 Оптимизация: добавлено {len([c for c in popular_from_usage if c in self.popular_emojis])} эмоджи в популярные")
    
    def get_stats(self) -> Dict:
        """Возвращает статистику базы данных"""
        return {
            'popular_count': len(self.popular_emojis),
            'basic_count': len(self.basic_emojis) if self.levels_loaded[2] else 'не загружено',
            'full_count': len(self.full_emojis) if self.levels_loaded[3] else 'не загружено',
            'youtube_count': len(self.youtube_emojis) if self.levels_loaded[4] else 'не загружено',
            'honey_club_count': len(self.honey_club_emojis) if self.levels_loaded[5] else 'не загружено',
            'total_usage': sum(self.usage_stats.values()),
            'unique_used': len(self.usage_stats),
            'levels_loaded': self.levels_loaded
        }
    
    def search_emojis(self, query: str, max_results: int = 20) -> Dict[str, str]:
        """Поиск эмоджи по запросу"""
        query = query.lower()
        results = {}
        
        # Поиск в популярных эмоджи
        for code, emoji in self.popular_emojis.items():
            if query in code.lower() and len(results) < max_results:
                results[code] = emoji
        
        # Поиск в базовых эмоджи если нужно больше результатов
        if len(results) < max_results:
            self._load_basic_emojis()
            for code, emoji in self.basic_emojis.items():
                if query in code.lower() and len(results) < max_results:
                    results[code] = emoji
        
        # Поиск в персональных эмоджи канала
        if len(results) < max_results:
            self._load_honey_club_emojis()
            for code, emoji in self.honey_club_emojis.items():
                if query in code.lower() and len(results) < max_results:
                    results[code] = emoji
        
        return results

# Глобальный экземпляр для использования
emoji_db = EmojiDatabase()

def convert_emojis(text: str, performance_mode: str = 'balanced') -> str:
    """
    Конвертирует эмоджи с выбором режима производительности
    
    Args:
        text (str): Текст для обработки
        performance_mode (str): Режим производительности
            'fast' - только популярные эмоджи (уровень 1)
            'balanced' - популярные + базовые (уровень 2) [по умолчанию]
            'complete' - все эмоджи кроме YouTube (уровень 3)
            'full' - все эмоджи включая YouTube (уровень 4)
            'channel' - все эмоджи включая персональные канала (уровень 5)
    
    Returns:
        str: Обработанный текст
    """
    level_map = {
        'fast': 1,
        'balanced': 2,
        'complete': 3,
        'full': 4,
        'channel': 5
    }
    
    max_level = level_map.get(performance_mode, 2)
    return emoji_db.convert_emojis(text, max_level)

def get_emoji_stats():
    """Возвращает статистику эмоджи базы"""
    return emoji_db.get_stats()

def search_emojis(query: str, max_results: int = 20):
    """Поиск эмоджи по запросу"""
    return emoji_db.search_emojis(query, max_results)

def optimize_emoji_performance():
    """Оптимизирует производительность на основе статистики использования"""
    emoji_db.optimize_popular_emojis()

if __name__ == "__main__":
    # Тестирование производительности
    test_text = "Привет :fire: :heart: :thumbsup: :grinning_face: :rocket: :party_popper:"
    
    safe_print("🧪 Тестирование производительности эмоджи базы")
    safe_print("=" * 50)
    
    # Тест быстрого режима
    start = time.time()
    result_fast = convert_emojis(test_text, 'fast')
    time_fast = time.time() - start
    safe_print(f"⚡ Быстрый режим: {time_fast:.4f}s")
    safe_print(f"   Результат: {result_fast}")
    
    # Тест сбалансированного режима
    start = time.time()
    result_balanced = convert_emojis(test_text, 'balanced')
    time_balanced = time.time() - start
    safe_print(f"⚖️ Сбалансированный режим: {time_balanced:.4f}s")
    safe_print(f"   Результат: {result_balanced}")
    
    # Статистика
    safe_print(f"\n📊 Статистика базы данных:")
    stats = get_emoji_stats()
    for key, value in stats.items():
        safe_print(f"   {key}: {value}")
    
    # Тест поиска
    safe_print(f"\n🔍 Поиск 'heart':")
    search_results = search_emojis('heart', 5)
    for code, emoji in search_results.items():
        safe_print(f"   {code}: {emoji}")
