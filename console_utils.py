#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Утилиты для корректного отображения эмоджи в консоли Windows
"""

import sys
import os
import locale
import codecs

def setup_console_encoding():
    """
    Настраивает кодировку консоли для корректного отображения эмоджи
    """
    try:
        # Способ 1: Установка UTF-8 кодировки для stdout/stderr
        if sys.platform.startswith('win'):
            # Для Windows 10+ можно использовать UTF-8
            try:
                # Пытаемся установить UTF-8 кодировку
                sys.stdout.reconfigure(encoding='utf-8')
                sys.stderr.reconfigure(encoding='utf-8')
                print("✅ UTF-8 кодировка установлена успешно")
                return True
            except (AttributeError, OSError):
                # Fallback для старых версий Python или Windows
                pass
        
        # Способ 2: Использование codecs для обертки stdout
        if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding.lower() != 'utf-8':
            try:
                # Оборачиваем stdout в UTF-8 writer
                sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
                sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
                print("✅ UTF-8 обертка установлена")
                return True
            except (AttributeError, OSError):
                pass
        
        # Способ 3: Установка переменной среды (требует перезапуска)
        if sys.platform.startswith('win'):
            os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        return False
        
    except Exception as e:
        print(f"⚠️ Не удалось настроить кодировку: {e}")
        return False

def safe_print(*args, **kwargs):
    """
    Безопасный вывод с обработкой ошибок кодировки
    """
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Если не удается вывести эмоджи, заменяем их на текстовые аналоги
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                # Заменяем эмоджи на текстовые аналоги
                safe_arg = replace_emojis_with_text(str(arg))
                safe_args.append(safe_arg)
            else:
                safe_args.append(arg)
        print(*safe_args, **kwargs)

def replace_emojis_with_text(text):
    """
    Заменяет эмоджи на текстовые аналоги для консоли
    """
    emoji_replacements = {
        '🔥': '[FIRE]',
        '❤️': '[HEART]',
        '👍': '[THUMBS_UP]',
        '👎': '[THUMBS_DOWN]',
        '😀': '[GRIN]',
        '😃': '[SMILE]',
        '😄': '[LAUGH]',
        '😁': '[BEAM]',
        '😆': '[SQUINT]',
        '😅': '[SWEAT]',
        '🤣': '[ROFL]',
        '😂': '[JOY]',
        '🙂': '[SLIGHT_SMILE]',
        '🙃': '[UPSIDE_DOWN]',
        '😉': '[WINK]',
        '😊': '[BLUSH]',
        '😇': '[HALO]',
        '🥰': '[LOVE]',
        '😍': '[HEART_EYES]',
        '🤩': '[STAR_STRUCK]',
        '😘': '[KISS]',
        '😗': '[KISS_FACE]',
        '☺️': '[SMILE_FACE]',
        '🤔': '[THINK]',
        '😐': '[NEUTRAL]',
        '😑': '[EXPRESSIONLESS]',
        '😶': '[NO_MOUTH]',
        '😏': '[SMIRK]',
        '😒': '[UNAMUSED]',
        '🙄': '[ROLL_EYES]',
        '😬': '[GRIMACE]',
        '😌': '[RELIEVED]',
        '😔': '[PENSIVE]',
        '😪': '[SLEEPY]',
        '😴': '[SLEEPING]',
        '😷': '[MASK]',
        '🥵': '[HOT]',
        '🥶': '[COLD]',
        '🥴': '[WOOZY]',
        '😵': '[DIZZY]',
        '🤯': '[EXPLODING_HEAD]',
        '🤠': '[COWBOY]',
        '🥳': '[PARTY]',
        '😎': '[COOL]',
        '🤓': '[NERD]',
        '😕': '[CONFUSED]',
        '😟': '[WORRIED]',
        '🙁': '[FROWN]',
        '☹️': '[FROWN_FACE]',
        '😮': '[OPEN_MOUTH]',
        '😯': '[HUSHED]',
        '😲': '[ASTONISHED]',
        '😳': '[FLUSHED]',
        '🥺': '[PLEADING]',
        '😢': '[CRY]',
        '😭': '[SOBBING]',
        '😱': '[SCREAM]',
        '😠': '[ANGRY]',
        '😡': '[RAGE]',
        '💀': '[SKULL]',
        '👋': '[WAVE]',
        '🤙': '[CALL_ME]',
        '💪': '[MUSCLE]',
        '👏': '[CLAP]',
        '🙌': '[RAISE_HANDS]',
        '🙏': '[PRAY]',
        '🧡': '[ORANGE_HEART]',
        '💛': '[YELLOW_HEART]',
        '💚': '[GREEN_HEART]',
        '💙': '[BLUE_HEART]',
        '💜': '[PURPLE_HEART]',
        '🖤': '[BLACK_HEART]',
        '🤍': '[WHITE_HEART]',
        '💔': '[BROKEN_HEART]',
        '💯': '[100]',
        '💥': '[BOOM]',
        '⭐': '[STAR]',
        '🌟': '[GLOWING_STAR]',
        '💎': '[GEM]',
        '👑': '[CROWN]',
        '🏆': '[TROPHY]',
        '🚀': '[ROCKET]',
        '💰': '[MONEY_BAG]',
        '🎁': '[GIFT]',
        '🎂': '[CAKE]',
        '🎉': '[PARTY_POPPER]',
        '🎊': '[CONFETTI]',
        '🎈': '[BALLOON]',
        '🎵': '[MUSIC_NOTE]',
        '🎶': '[MUSIC_NOTES]',
        '✨': '[SPARKLES]',
        '⚡': '[LIGHTNING]',
        '🔍': '[SEARCH]',
        '📊': '[CHART]',
        '⚠️': '[WARNING]',
        '✅': '[CHECK]',
        '❌': '[X]',
        '🧪': '[TEST_TUBE]',
        '⚖️': '[SCALE]',
        '⚡': '[FAST]',
        '🐍': '[SNAKE]',
        '🟨': '[YELLOW_SQUARE]',
        '📄': '[PAGE]',
        '📥': '[INBOX]',
        '🔄': '[ARROWS]',
        '➕': '[PLUS]',
        '⏱️': '[STOPWATCH]',
        '📝': '[MEMO]',
        '📋': '[CLIPBOARD]'
    }
    
    result = text
    for emoji, replacement in emoji_replacements.items():
        result = result.replace(emoji, replacement)
    
    return result

def print_with_fallback(*args, **kwargs):
    """
    Печать с автоматическим fallback на текстовые аналоги
    """
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Конвертируем все аргументы в безопасный формат
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_args.append(replace_emojis_with_text(arg))
            else:
                safe_args.append(str(arg))
        print(*safe_args, **kwargs)

def test_emoji_support():
    """
    Тестирует поддержку эмоджи в консоли
    """
    test_emojis = ['🔥', '❤️', '👍', '😀', '🚀', '⭐', '💯']
    
    print("Тестирование поддержки эмоджи в консоли:")
    print("-" * 50)
    
    for emoji in test_emojis:
        try:
            print(f"Тест эмоджи: {emoji}")
        except UnicodeEncodeError:
            print(f"Тест эмоджи: {replace_emojis_with_text(emoji)} (fallback)")
    
    print("-" * 50)
    print("Информация о кодировке:")
    print(f"  stdout encoding: {getattr(sys.stdout, 'encoding', 'unknown')}")
    print(f"  stderr encoding: {getattr(sys.stderr, 'encoding', 'unknown')}")
    print(f"  locale: {locale.getpreferredencoding()}")
    print(f"  platform: {sys.platform}")

if __name__ == "__main__":
    print("Настройка кодировки консоли...")
    
    # Пытаемся настроить кодировку
    success = setup_console_encoding()
    
    if success:
        print("Кодировка настроена успешно!")
    else:
        print("Используется fallback режим с текстовыми аналогами")
    
    # Тестируем поддержку эмоджи
    test_emoji_support()
