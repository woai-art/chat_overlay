#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тест производительности эмоджи базы данных
"""

import time
import sys

# Настраиваем кодировку консоли
try:
    from console_utils import setup_console_encoding, print_with_fallback
    setup_console_encoding()
    safe_print = print_with_fallback
except ImportError:
    safe_print = print

from emoji_database_enhanced import convert_emojis, get_emoji_stats, search_emojis

def test_performance():
    """Тестирует производительность различных режимов"""
    
    # Тестовые тексты разной сложности
    test_cases = [
        {
            'name': 'Простой текст',
            'text': 'Привет :fire: :heart: :thumbsup:'
        },
        {
            'name': 'Средний текст',
            'text': 'Привет :fire: :heart: :thumbsup: :grinning_face: :rocket: :party_popper: :clap: :wave: :100:'
        },
        {
            'name': 'Сложный текст',
            'text': 'Привет :fire: :heart: :thumbsup: :grinning_face: :rocket: :party_popper: :clap: :wave: :100: :star: :crown: :trophy: :gem: :musical_note: :birthday_cake: :gift: :balloon: :confetti_ball: :collision:'
        },
        {
            'name': 'Текст с ASCII эмотиконами',
            'text': 'Привет :) :D :P ;) <3 :( :O :|'
        },
        {
            'name': 'Текст со сленгом',
            'text': 'Это :pogchamp: :kappa: :pepehands: :omegalul: :gigachad: :based: :cringe: :sus: :no_cap: :bussin:'
        },
        {
            'name': 'Текст с персональными эмоджи',
            'text': 'Привет :hello: Как дела? :love: Не злись :angry: Будь милым :cute: :Kaif: :evil:'
        }
    ]
    
    modes = [
        ('fast', 'Быстрый режим (только популярные)'),
        ('balanced', 'Сбалансированный режим (популярные + базовые)'),
        ('complete', 'Полный режим (все кроме YouTube)'),
        ('full', 'Максимальный режим (включая YouTube)'),
        ('channel', 'Канальный режим (все + персональные эмоджи)')
    ]
    
    safe_print("=" * 80)
    safe_print("🧪 ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ ЭМОДЖИ БАЗЫ ДАННЫХ")
    safe_print("=" * 80)
    
    # Статистика базы данных
    safe_print("\n📊 Статистика базы данных:")
    stats = get_emoji_stats()
    for key, value in stats.items():
        safe_print(f"  {key}: {value}")
    
    safe_print("\n" + "-" * 80)
    safe_print("⚡ ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ")
    safe_print("-" * 80)
    
    results = {}
    
    for test_case in test_cases:
        safe_print(f"\n📝 {test_case['name']}:")
        safe_print(f"   Длина текста: {len(test_case['text'])} символов")
        
        results[test_case['name']] = {}
        
        for mode_code, mode_name in modes:
            # Прогрев
            convert_emojis(test_case['text'], mode_code)
            
            # Измерение времени
            times = []
            for _ in range(10):  # 10 итераций для точности
                start = time.time()
                result = convert_emojis(test_case['text'], mode_code)
                end = time.time()
                times.append(end - start)
            
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            results[test_case['name']][mode_code] = {
                'avg_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'result_length': len(result)
            }
            
            safe_print(f"   {mode_name}:")
            safe_print(f"     Среднее время: {avg_time*1000:.2f}ms")
            safe_print(f"     Мин/Макс: {min_time*1000:.2f}ms / {max_time*1000:.2f}ms")
            safe_print(f"     Длина результата: {len(result)} символов")
    
    # Анализ результатов
    safe_print("\n" + "=" * 80)
    safe_print("📈 АНАЛИЗ РЕЗУЛЬТАТОВ")
    safe_print("=" * 80)
    
    # Сравнение режимов
    safe_print("\nСравнение режимов (среднее время в ms):")
    safe_print(f"{'Тест':<25} {'Быстрый':<10} {'Сбаланс.':<10} {'Полный':<10} {'Макс.':<10} {'Канал':<10}")
    safe_print("-" * 80)
    
    for test_name, test_results in results.items():
        row = f"{test_name:<25}"
        for mode_code, _ in modes:
            if mode_code in test_results:
                time_ms = test_results[mode_code]['avg_time'] * 1000
                row += f"{time_ms:<10.2f}"
            else:
                row += f"{'N/A':<10}"
        safe_print(row)
    
    # Рекомендации
    safe_print("\n" + "=" * 80)
    safe_print("💡 РЕКОМЕНДАЦИИ ПО ПРОИЗВОДИТЕЛЬНОСТИ")
    safe_print("=" * 80)
    
    # Находим самый быстрый режим для каждого теста
    for test_name, test_results in results.items():
        fastest_mode = min(test_results.items(), key=lambda x: x[1]['avg_time'])
        fastest_time = fastest_mode[1]['avg_time'] * 1000
        
        safe_print(f"\n{test_name}:")
        safe_print(f"  Рекомендуемый режим: {dict(modes)[fastest_mode[0]]}")
        safe_print(f"  Время обработки: {fastest_time:.2f}ms")
        
        # Предупреждения о производительности
        if fastest_time > 10:
            safe_print(f"  ⚠️  ВНИМАНИЕ: Время обработки > 10ms может влиять на производительность чата")
        elif fastest_time > 5:
            safe_print(f"  ⚠️  Время обработки > 5ms - следите за производительностью")
        else:
            safe_print(f"  ✅ Отличная производительность")
    
    # Общие рекомендации
    safe_print(f"\n📋 ОБЩИЕ РЕКОМЕНДАЦИИ:")
    safe_print(f"  • Для максимальной производительности используйте 'fast' режим")
    safe_print(f"  • Для баланса функций/производительности используйте 'balanced' режим")
    safe_print(f"  • Режимы 'complete' и 'full' используйте только при необходимости")
    safe_print(f"  • Режим 'channel' используйте для персональных эмоджи канала")
    safe_print(f"  • Время обработки > 10ms может замедлить чат при большом потоке сообщений")
    
    return results

def test_search_performance():
    """Тестирует производительность поиска эмоджи"""
    safe_print("\n" + "=" * 80)
    safe_print("🔍 ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ ПОИСКА")
    safe_print("=" * 80)
    
    search_queries = ['heart', 'face', 'hand', 'fire', 'star', 'smile', 'cry', 'love']
    
    for query in search_queries:
        start = time.time()
        results = search_emojis(query, 10)
        end = time.time()
        
        search_time = (end - start) * 1000
        safe_print(f"Поиск '{query}': {search_time:.2f}ms, найдено: {len(results)} эмоджи")

def test_memory_usage():
    """Тестирует использование памяти"""
    safe_print("\n" + "=" * 80)
    safe_print("💾 ТЕСТ ИСПОЛЬЗОВАНИЯ ПАМЯТИ")
    safe_print("=" * 80)
    
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Память до загрузки
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        safe_print(f"Память до загрузки: {memory_before:.2f} MB")
        
        # Загружаем все уровни
        convert_emojis("test", 'full')
        
        # Память после загрузки
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_diff = memory_after - memory_before
        
        safe_print(f"Память после загрузки: {memory_after:.2f} MB")
        safe_print(f"Использовано дополнительно: {memory_diff:.2f} MB")
        
        if memory_diff > 50:
            safe_print("⚠️  ВНИМАНИЕ: Высокое использование памяти")
        elif memory_diff > 20:
            safe_print("⚠️  Умеренное использование памяти")
        else:
            safe_print("✅ Низкое использование памяти")
            
    except ImportError:
        safe_print("psutil не установлен - пропускаем тест памяти")
        safe_print("Установите: pip install psutil")

if __name__ == "__main__":
    try:
        # Основной тест производительности
        results = test_performance()
        
        # Тест поиска
        test_search_performance()
        
        # Тест памяти
        test_memory_usage()
        
        safe_print("\n" + "=" * 80)
        safe_print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        safe_print("=" * 80)
        
    except KeyboardInterrupt:
        safe_print("\nТестирование прервано пользователем")
    except Exception as e:
        safe_print(f"\nОшибка во время тестирования: {e}")
        sys.exit(1)
