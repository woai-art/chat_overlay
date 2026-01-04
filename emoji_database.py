#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
База данных эмоджи для YouTube Live Chat Parser
ОБНОВЛЕНО: Теперь поддерживает улучшенную систему с YouTube эмоджи
Содержит 3,686+ эмоджи для конвертации текстовых кодов в Unicode символы
"""

# Импортируем улучшенную систему эмоджи
try:
    from emoji_database_enhanced import convert_emojis as enhanced_convert, get_emoji_stats, search_emojis
    ENHANCED_AVAILABLE = True
    print("✅ Загружена улучшенная система эмоджи с поддержкой YouTube эмоджи")
except ImportError:
    ENHANCED_AVAILABLE = False
    print("⚠️ Используется базовая версия эмоджи")

# =============================================================================
# БАЗА ДАННЫХ ЭМОДЖИ
# =============================================================================

EMOJI_DATABASE = {
    # Лица и эмоции
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
    ':kissing_face_with_closed_eyes:': '😚',
    ':kissing_face_with_smiling_eyes:': '😙',
    ':face_savoring_food:': '😋',
    ':face_with_tongue:': '😛',
    ':winking_face_with_tongue:': '😜',
    ':zany_face:': '🤪',
    ':squinting_face_with_tongue:': '😝',
    ':money_mouth_face:': '🤑',
    ':hugging_face:': '🤗',
    ':face_with_hand_over_mouth:': '🤭',
    ':shushing_face:': '🤫',
    ':thinking_face:': '🤔',
    ':zipper_mouth_face:': '🤐',
    ':face_with_raised_eyebrow:': '🤨',
    ':neutral_face:': '😐',
    ':expressionless_face:': '😑',
    ':face_without_mouth:': '😶',
    ':smirking_face:': '😏',
    ':unamused_face:': '😒',
    ':face_with_rolling_eyes:': '🙄',
    ':grimacing_face:': '😬',
    ':lying_face:': '🤥',
    ':relieved_face:': '😌',
    ':pensive_face:': '😔',
    ':sleepy_face:': '😪',
    ':drooling_face:': '🤤',
    ':sleeping_face:': '😴',
    ':face_with_medical_mask:': '😷',
    ':face_with_thermometer:': '🤒',
    ':face_with_head_bandage:': '🤕',
    ':nauseated_face:': '🤢',
    ':face_vomiting:': '🤮',
    ':sneezing_face:': '🤧',
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
    ':frowning_face_with_open_mouth:': '😦',
    ':anguished_face:': '😧',
    ':fearful_face:': '😨',
    ':anxious_face_with_sweat:': '😰',
    ':sad_but_relieved_face:': '😥',
    ':crying_face:': '😢',
    ':loudly_crying_face:': '😭',
    ':face_screaming_in_fear:': '😱',
    ':confounded_face:': '😖',
    ':persevering_face:': '😣',
    ':disappointed_face:': '😞',
    ':downcast_face_with_sweat:': '😓',
    ':weary_face:': '😩',
    ':tired_face:': '😫',
    ':face_with_steam_from_nose:': '😤',
    ':pouting_face:': '😡',
    ':angry_face:': '😠',
    ':face_with_symbols_on_mouth:': '🤬',
    ':smiling_face_with_horns:': '😈',
    ':angry_face_with_horns:': '👿',
    ':skull:': '💀',
    ':skull_and_crossbones:': '☠️',

    # Жесты и руки
    ':thumbs_up:': '👍',
    ':thumbs_down:': '👎',
    ':ok_hand:': '👌',
    ':victory_hand:': '✌️',
    ':crossed_fingers:': '🤞',
    ':raised_hand:': '✋',
    ':vulcan_salute:': '🖖',
    ':waving_hand:': '👋',
    ':call_me_hand:': '🤙',
    ':flexed_biceps:': '💪',
    ':clapping_hands:': '👏',
    ':raising_hands:': '🙌',
    ':open_hands:': '👐',
    ':folded_hands:': '🙏',
    ':writing_hand:': '✍️',
    ':nail_polish:': '💅',
    ':selfie:': '🤳',

    # Сердца и любовь
    ':red_heart:': '❤️',
    ':orange_heart:': '🧡',
    ':yellow_heart:': '💛',
    ':green_heart:': '💚',
    ':blue_heart:': '💙',
    ':purple_heart:': '💜',
    ':brown_heart:': '🤎',
    ':black_heart:': '🖤',
    ':white_heart:': '🤍',
    ':heart_with_arrow:': '💘',
    ':heart_with_ribbon:': '💝',
    ':sparkling_heart:': '💖',
    ':growing_heart:': '💗',
    ':beating_heart:': '💓',
    ':revolving_hearts:': '💞',
    ':two_hearts:': '💕',
    ':heart_decoration:': '💟',
    ':heart_exclamation:': '❣️',
    ':broken_heart:': '💔',

    # Животные
    ':dog_face:': '🐶',
    ':cat_face:': '🐱',
    ':mouse_face:': '🐭',
    ':hamster_face:': '🐹',
    ':rabbit_face:': '🐰',
    ':fox_face:': '🦊',
    ':bear_face:': '🐻',
    ':panda_face:': '🐼',
    ':koala:': '🐨',
    ':tiger_face:': '🐯',
    ':lion:': '🦁',
    ':cow_face:': '🐮',
    ':pig_face:': '🐷',
    ':frog:': '🐸',
    ':monkey_face:': '🐵',
    ':chicken:': '🐔',
    ':penguin:': '🐧',
    ':bird:': '🐦',
    ':baby_chick:': '🐤',
    ':hatching_chick:': '🐣',
    ':front_facing_baby_chick:': '🐥',
    ':duck:': '🦆',
    ':eagle:': '🦅',
    ':owl:': '🦉',
    ':bat:': '🦇',
    ':wolf:': '🐺',
    ':boar:': '🐗',
    ':horse_face:': '🐴',
    ':unicorn:': '🦄',
    ':zebra:': '🦓',
    ':deer:': '🦌',
    ':elephant:': '🐘',
    ':rhinoceros:': '🦏',
    ':hippopotamus:': '🦛',
    ':giraffe:': '🦒',
    ':llama:': '🦙',

    # Символы и объекты
    ':fire:': '🔥',
    ':hundred_points:': '💯',
    ':collision:': '💥',
    ':sweat_droplets:': '💦',
    ':star:': '⭐',
    ':glowing_star:': '🌟',
    ':dizzy:': '💫',
    ':speech_balloon:': '💬',
    ':thought_balloon:': '💭',
    ':zzz:': '💤',
    ':gem:': '💎',
    ':crown:': '👑',
    ':trophy:': '🏆',
    ':medal:': '🏅',
    ':rocket:': '🚀',
    ':bomb:': '💣',
    ':money_bag:': '💰',
    ':dollar_banknote:': '💵',
    ':euro_banknote:': '💶',
    ':pound_banknote:': '💷',
    ':yen_banknote:': '💴',
    ':credit_card:': '💳',
    ':gift:': '🎁',
    ':birthday_cake:': '🎂',
    ':party_popper:': '🎉',
    ':confetti_ball:': '🎊',
    ':balloon:': '🎈',
    ':musical_note:': '🎵',
    ':musical_notes:': '🎶',
    ':microphone:': '🎤',
    ':headphone:': '🎧',
    ':radio:': '📻',
    ':saxophone:': '🎷',
    ':guitar:': '🎸',
    ':musical_keyboard:': '🎹',
    ':trumpet:': '🎺',
    ':violin:': '🎻',

    # Еда и напитки
    ':grapes:': '🍇',
    ':melon:': '🍈',
    ':watermelon:': '🍉',
    ':tangerine:': '🍊',
    ':lemon:': '🍋',
    ':banana:': '🍌',
    ':pineapple:': '🍍',
    ':mango:': '🥭',
    ':red_apple:': '🍎',
    ':green_apple:': '🍏',
    ':pear:': '🍐',
    ':peach:': '🍑',
    ':cherries:': '🍒',
    ':strawberry:': '🍓',
    ':kiwi_fruit:': '🥝',
    ':tomato:': '🍅',
    ':coconut:': '🥥',
    ':avocado:': '🥑',
    ':eggplant:': '🍆',
    ':potato:': '🥔',
    ':carrot:': '🥕',
    ':corn:': '🌽',
    ':hot_pepper:': '🌶️',
    ':cucumber:': '🥒',
    ':leafy_greens:': '🥬',
    ':broccoli:': '🥦',
    ':garlic:': '🧄',
    ':onion:': '🧅',
    ':mushroom:': '🍄',
    ':peanuts:': '🥜',
    ':chestnut:': '🌰',
    ':bread:': '🍞',
    ':croissant:': '🥐',
    ':baguette_bread:': '🥖',
    ':pretzel:': '🥨',
    ':bagel:': '🥯',
    ':pancakes:': '🥞',
    ':waffle:': '🧇',
    ':cheese_wedge:': '🧀',
    ':meat_on_bone:': '🍖',
    ':poultry_leg:': '🍗',
    ':cut_of_meat:': '🥩',
    ':bacon:': '🥓',
    ':hamburger:': '🍔',
    ':french_fries:': '🍟',
    ':pizza:': '🍕',
    ':hot_dog:': '🌭',
    ':sandwich:': '🥪',
    ':taco:': '🌮',
    ':burrito:': '🌯',
    ':egg:': '🥚',
    ':cooking:': '🍳',
    ':pot_of_food:': '🍲',
    ':bowl_with_spoon:': '🥣',
    ':green_salad:': '🥗',
    ':popcorn:': '🍿',
    ':canned_food:': '🥫',

    # Напитки
    ':baby_bottle:': '🍼',
    ':glass_of_milk:': '🥛',
    ':hot_beverage:': '☕',
    ':teacup_without_handle:': '🍵',
    ':sake:': '🍶',
    ':bottle_with_popping_cork:': '🍾',
    ':wine_glass:': '🍷',
    ':cocktail_glass:': '🍸',
    ':tropical_drink:': '🍹',
    ':beer_mug:': '🍺',
    ':clinking_beer_mugs:': '🍻',
    ':clinking_glasses:': '🥂',
    ':tumbler_glass:': '🥃',
    ':cup_with_straw:': '🥤',
    ':bubble_tea:': '🧋',
    ':beverage_box:': '🧃',
    ':ice:': '🧊',

    # Простые эмотиконы (ASCII)
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
    ':bestie:': '👯',
    ':queen:': '👑',
    ':king:': '👑',
    ':icon:': '⭐',
    ':legend:': '🏆',
    ':goat:': '🐐',
    ':mood:': '😌',
    ':vibe:': '✨',
    ':energy:': '⚡',
    ':aura:': '✨',
    ':flex:': '💪',
    ':drip:': '💧',
    ':fire_emoji:': '🔥',
    ':lit:': '🔥',
    ':bet:': '💯',
    ':say_less:': '🤐',
    ':main_character:': '⭐',
    ':that_part:': '💯',
    ':understood_the_assignment:': '✅',
    ':living_for_this:': '😍',
    ':obsessed:': '😍',
    ':not_me:': '🙈',
    ':the_way:': '😭',
    ':please:': '🙏',
    ':help:': '😭',
    ':crying:': '😭',
    ':dead:': '💀',
    ':deceased:': '💀',
    ':gone:': '💀',
    ':sent_me:': '💀',
    ':took_me_out:': '💀',
    ':screaming:': '😱',
    ':shook:': '😱',
    ':gagged:': '😱',
    ':wig_snatched:': '💇',
    ':scalped:': '💇',
    ':bald:': '👨‍🦲',
    ':no_hair:': '👨‍🦲'
}

def convert_emojis(text, performance_mode='balanced'):
    """
    Конвертирует текстовые коды эмоджи в Unicode символы
    ОБНОВЛЕНО: Поддерживает улучшенную систему с YouTube эмоджи
    
    Args:
        text (str): Исходный текст с кодами эмоджи
        performance_mode (str): Режим производительности
            'fast' - только популярные эмоджи
            'balanced' - популярные + базовые (рекомендуется)
            'complete' - все эмоджи кроме YouTube
            'full' - все эмоджи включая YouTube
        
    Returns:
        str: Текст с замененными эмоджи
    """
    if not text:
        return text
    
    # Используем улучшенную систему если доступна
    if ENHANCED_AVAILABLE:
        return enhanced_convert(text, performance_mode)
    
    # Fallback на базовую версию
    result = text
    
    # Проходим по всем эмоджи в базе данных
    for code, emoji in EMOJI_DATABASE.items():
        # Заменяем все вхождения кода на эмоджи
        result = result.replace(code, emoji)
    
    return result

def get_emoji_count():
    """Возвращает количество эмоджи в базе данных"""
    if ENHANCED_AVAILABLE:
        stats = get_emoji_stats()
        return stats.get('total_count', len(EMOJI_DATABASE))
    return len(EMOJI_DATABASE)

def get_emoji_by_code(code):
    """Возвращает эмоджи по коду или None если не найден"""
    return EMOJI_DATABASE.get(code)

def search_emojis_basic(query):
    """Базовый поиск эмоджи по части кода"""
    query = query.lower()
    return {code: emoji for code, emoji in EMOJI_DATABASE.items() if query in code.lower()}

# Переопределяем search_emojis для использования улучшенной версии
if not ENHANCED_AVAILABLE:
    def search_emojis(query, max_results=20):
        """Поиск эмоджи по части кода (базовая версия)"""
        return search_emojis_basic(query)

if __name__ == "__main__":
    # Тест функций
    try:
        from console_utils import safe_print
    except ImportError:
        safe_print = print
    
    safe_print(f"📊 Всего эмоджи в базе: {get_emoji_count()}")
    
    # Тест базовых эмоджи
    safe_print(f"🔥 Тест базовых эмоджи: {convert_emojis('Привет :fire: :heart: :thumbsup:', 'fast')}")
    
    # Тест YouTube эмоджи если доступны
    if ENHANCED_AVAILABLE:
        youtube_test = convert_emojis('YouTube эмоджи: :hand-pink-waving: :face-blue-smiling:', 'full')
        safe_print(f"🎬 Тест YouTube эмоджи: {youtube_test}")
        
        # Статистика улучшенной системы
        stats = get_emoji_stats()
        safe_print(f"📈 Статистика улучшенной системы:")
        for key, value in stats.items():
            safe_print(f"   {key}: {value}")
    
    # Тест поиска
    search_results = search_emojis('heart', 5) if ENHANCED_AVAILABLE else search_emojis_basic('heart')
    safe_print(f"🔍 Поиск 'heart': найдено {len(search_results)} эмоджи")
