#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Персональные эмоджи для канала Honey Club
Уровень 5: Специфичные эмоджи канала
"""

import os
from pathlib import Path

# Настраиваем кодировку консоли
try:
    from console_utils import setup_console_encoding, print_with_fallback
    setup_console_encoding()
    safe_print = print_with_fallback
except ImportError:
    safe_print = print

class HoneyClubEmojis:
    """Класс для управления персональными эмоджи канала Honey Club"""
    
    def __init__(self):
        self.emoji_path = Path("./Emoji-Honey-Club")  # Локальная папка в проекте
        self.honey_club_emojis = {}
        self.base_url = "./Emoji-Honey-Club/"  # Относительный путь для веб-интерфейса
        
        # Загружаем эмоджи при инициализации
        self._load_honey_club_emojis()
    
    def _load_honey_club_emojis(self):
        """Загружает персональные эмоджи канала Honey Club"""
        if not self.emoji_path.exists():
            safe_print(f"⚠️ Папка с эмоджи не найдена: {self.emoji_path}")
            return
        
        # Маппинг имен файлов на коды эмоджи (согласно скриншоту)
        emoji_mapping = {
            'angry.png': ':angry:',
            'shout.png': ':shout:',
            'hello.png': ':hello:',
            'evil.png': ':evil:',
            'love.png': ':love:',
            'hungover.png': ':hungover:',
            'vomit.png': ':vomit:',
            'сute.png': ':cute:',  # Обратите внимание на кириллическую 'с'
            'monster.png': ':monster:',
            'HurryUp.png': ':HurryUp:',
            'Kaif.png': ':Kaif:',
            'Zlost.png': ':Zlost:',
            'dislike.png': ':dislike:',
            'comeon.png': ':comeon:',
            'hugs.png': ':hugs:'  # Если есть такой файл
        }
        
        # Проверяем какие файлы реально существуют
        existing_files = [f.name for f in self.emoji_path.glob("*.png")]
        
        for filename, emoji_code in emoji_mapping.items():
            if filename in existing_files:
                # Создаем HTML для эмоджи
                img_path = f"{self.base_url}{filename}"
                emoji_html = f'<img src="{img_path}" alt="{emoji_code}" class="honey-club-emoji" title="{emoji_code}">'
                self.honey_club_emojis[emoji_code] = emoji_html
        
        safe_print(f"🍯 Загружено {len(self.honey_club_emojis)} эмоджи канала Honey Club")
        
        # Выводим список загруженных эмоджи
        if self.honey_club_emojis:
            safe_print("📝 Доступные эмоджи канала:")
            for code in sorted(self.honey_club_emojis.keys()):
                safe_print(f"   {code}")
    
    def get_emoji_html(self, code):
        """Возвращает HTML для эмоджи по коду"""
        return self.honey_club_emojis.get(code)
    
    def get_all_emojis(self):
        """Возвращает все эмоджи канала"""
        return self.honey_club_emojis.copy()
    
    def search_emojis(self, query, max_results=10):
        """Поиск эмоджи канала по запросу"""
        query = query.lower()
        results = {}
        count = 0
        
        for code, html in self.honey_club_emojis.items():
            if query in code.lower() and count < max_results:
                results[code] = html
                count += 1
        
        return results
    
    def convert_text(self, text):
        """Конвертирует коды эмоджи канала в HTML"""
        if not text or not self.honey_club_emojis:
            return text
        
        result = text
        for code, html in self.honey_club_emojis.items():
            result = result.replace(code, html)
        
        return result
    
    def get_stats(self):
        """Возвращает статистику эмоджи канала"""
        return {
            'honey_club_count': len(self.honey_club_emojis),
            'emoji_path': str(self.emoji_path),
            'base_url': self.base_url,
            'available_emojis': list(self.honey_club_emojis.keys())
        }
    
    def generate_css(self):
        """Генерирует CSS для эмоджи канала"""
        css = """
/* Стили для эмоджи канала Honey Club */
.honey-club-emoji {
    width: 28px;
    height: 28px;
    vertical-align: middle;
    margin: 0 2px;
    border-radius: 4px;
    display: inline-block;
    transition: transform 0.2s ease, filter 0.2s ease;
}

.honey-club-emoji:hover {
    transform: scale(1.3);
    filter: brightness(1.1);
    cursor: pointer;
}

/* Специальные эффекты для разных эмоций */
.honey-club-emoji[alt=":angry:"] {
    filter: hue-rotate(0deg);
}

.honey-club-emoji[alt=":love:"] {
    filter: hue-rotate(300deg) saturate(1.2);
}

.honey-club-emoji[alt=":evil:"] {
    filter: hue-rotate(270deg) contrast(1.1);
}

.honey-club-emoji[alt=":cute:"] {
    filter: hue-rotate(30deg) saturate(1.1);
}

/* Анимация для особых эмоджи */
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-2px); }
    75% { transform: translateX(2px); }
}

.honey-club-emoji[alt=":angry:"]:hover {
    animation: shake 0.5s ease-in-out;
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-3px); }
}

.honey-club-emoji[alt=":hello:"]:hover {
    animation: bounce 0.6s ease-in-out;
}
"""
        return css
    
    def generate_family_name_suggestions(self):
        """Генерирует предложения для family name на основе эмоджи"""
        suggestions = [
            "Hbadger",  # Как на скриншоте
            "HoneyClub",
            "HoneyBadger",
            "HClub",
            "Honey",
            "BadgerClub"
        ]
        return suggestions

# Глобальный экземпляр
honey_club = HoneyClubEmojis()

def get_honey_club_emojis():
    """Возвращает все эмоджи канала Honey Club"""
    return honey_club.get_all_emojis()

def convert_honey_club_emojis(text):
    """Конвертирует эмоджи канала Honey Club в тексте"""
    return honey_club.convert_text(text)

def search_honey_club_emojis(query, max_results=10):
    """Поиск эмоджи канала Honey Club"""
    return honey_club.search_emojis(query, max_results)

def get_honey_club_stats():
    """Возвращает статистику эмоджи канала"""
    return honey_club.get_stats()

if __name__ == "__main__":
    # Тестирование
    safe_print("🍯 Тестирование эмоджи канала Honey Club")
    safe_print("=" * 50)
    
    # Статистика
    stats = get_honey_club_stats()
    safe_print(f"📊 Статистика:")
    for key, value in stats.items():
        if key != 'available_emojis':
            safe_print(f"   {key}: {value}")
    
    # Тест конвертации
    test_text = "Привет :hello: Как дела? :love: Не злись :angry: Будь милым :cute:"
    safe_print(f"\n🧪 Тест конвертации:")
    safe_print(f"   Исходный текст: {test_text}")
    result = convert_honey_club_emojis(test_text)
    safe_print(f"   Результат: {result}")
    
    # Тест поиска
    safe_print(f"\n🔍 Поиск 'love':")
    search_results = search_honey_club_emojis('love')
    for code, html in search_results.items():
        safe_print(f"   {code}")
    
    # Генерация CSS
    safe_print(f"\n🎨 CSS сгенерирован для стилизации эмоджи")
    
    # Предложения для family name
    safe_print(f"\n💡 Предложения для family name:")
    suggestions = honey_club.generate_family_name_suggestions()
    for suggestion in suggestions:
        safe_print(f"   {suggestion}")
