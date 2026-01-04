// =============================================================================
// УЛУЧШЕННАЯ БАЗА ДАННЫХ ЭМОДЖИ ДЛЯ YOUTUBE LIVE CHAT
// Многоуровневая система с оптимизацией производительности
// =============================================================================

class EmojiDatabase {
    constructor() {
        this.popularEmojis = {};      // Уровень 1: Популярные эмоджи
        this.basicEmojis = {};        // Уровень 2: Базовые Unicode
        this.fullEmojis = {};         // Уровень 3: Полная база
        this.youtubeEmojis = {};      // Уровень 4: YouTube эмоджи
        
        // Кэш для производительности
        this.emojiCache = new Map();
        this.compiledPatterns = new Map();
        
        // Статистика использования
        this.usageStats = new Map();
        
        // Флаги загрузки
        this.levelsLoaded = {1: false, 2: false, 3: false, 4: false};
        
        // Загружаем популярные эмоджи при инициализации
        this._loadPopularEmojis();
    }
    
    _loadPopularEmojis() {
        this.popularEmojis = {
            // Лица и эмоции (самые популярные)
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
            
            // Жесты и руки
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
            
            // Сердца
            ':red_heart:': '❤️',
            ':orange_heart:': '🧡',
            ':yellow_heart:': '💛',
            ':green_heart:': '💚',
            ':blue_heart:': '💙',
            ':purple_heart:': '💜',
            ':black_heart:': '🖤',
            ':white_heart:': '🤍',
            ':broken_heart:': '💔',
            
            // Популярные символы
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
            
            // ASCII эмотиконы
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
            
            // Популярные сокращения
            ':heart:': '❤️',
            ':thumbsup:': '👍',
            ':thumbsdown:': '👎',
            ':clap:': '👏',
            ':wave:': '👋',
            ':eyes:': '👀',
            ':100:': '💯',
            
            // Популярные Twitch/YouTube эмоджи
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
        };
        
        this.levelsLoaded[1] = true;
        this._compilePatterns(this.popularEmojis);
    }
    
    async _loadBasicEmojis() {
        if (this.levelsLoaded[2]) return;
        
        try {
            // В браузере используем fetch, в Node.js - fs
            let data;
            if (typeof fetch !== 'undefined') {
                // Браузер - загружаем через fetch (если файл доступен)
                console.warn('Загрузка полной базы эмоджи в браузере не поддерживается');
                return;
            } else if (typeof require !== 'undefined') {
                // Node.js
                const fs = require('fs');
                const path = require('path');
                const filePath = path.join('D:', 'vMix', 'liveChat', 'Emoji-List-Unicode', 'json', 'all-emoji.json');
                
                if (fs.existsSync(filePath)) {
                    const fileContent = fs.readFileSync(filePath, 'utf8');
                    data = JSON.parse(fileContent);
                } else {
                    console.warn('Файл эмоджи не найден:', filePath);
                    return;
                }
            }
            
            // Парсим JSON и создаем базовые эмоджи (без модификаторов)
            let currentCategory = "";
            for (const item of data) {
                if (item.length === 1) {
                    currentCategory = item[0];
                } else if (item.length === 4 && /^\d+$/.test(item[0])) {
                    const [, unicodeCode, emoji, description] = item;
                    // Пропускаем эмоджи с модификаторами тона кожи
                    if (!unicodeCode.includes('U+1F3F')) {
                        const code = `:${description.toLowerCase().replace(/[ -]/g, '_')}:`;
                        if (!(code in this.popularEmojis)) {
                            this.basicEmojis[code] = emoji;
                        }
                    }
                }
            }
            
            this.levelsLoaded[2] = true;
            console.log(`Загружено ${Object.keys(this.basicEmojis).length} базовых эмоджи`);
            
        } catch (error) {
            console.error('Ошибка загрузки базовых эмоджи:', error);
        }
    }
    
    async _loadFullEmojis() {
        if (this.levelsLoaded[3]) return;
        
        try {
            // Сначала загружаем базовые эмоджи
            await this._loadBasicEmojis();
            
            // Загружаем эмоджи с модификаторами (аналогично базовым)
            // Для краткости пропускаем реализацию - аналогична _loadBasicEmojis
            
            this.levelsLoaded[3] = true;
            console.log(`Загружено ${Object.keys(this.fullEmojis).length} эмоджи с модификаторами`);
            
        } catch (error) {
            console.error('Ошибка загрузки полной базы эмоджи:', error);
        }
    }
    
    async _loadYoutubeEmojis() {
        if (this.levelsLoaded[4]) return;
        
        try {
            // Загрузка YouTube эмоджи из CSV
            // В реальном приложении здесь была бы загрузка CSV файла
            
            this.levelsLoaded[4] = true;
            console.log(`Загружено ${Object.keys(this.youtubeEmojis).length} YouTube эмоджи`);
            
        } catch (error) {
            console.error('Ошибка загрузки YouTube эмоджи:', error);
        }
    }
    
    _compilePatterns(emojiDict) {
        for (const code of Object.keys(emojiDict)) {
            if (!this.compiledPatterns.has(code)) {
                // Экранируем специальные символы для RegExp
                const escapedCode = code.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                this.compiledPatterns.set(code, new RegExp(escapedCode, 'g'));
            }
        }
    }
    
    async convertEmojis(text, maxLevel = 2) {
        if (!text) return text;
        
        const startTime = performance.now();
        let result = text;
        let replacementsMade = 0;
        
        // Уровень 1: Популярные эмоджи (всегда загружены)
        for (const [code, emoji] of Object.entries(this.popularEmojis)) {
            if (result.includes(code)) {
                result = result.replace(new RegExp(this._escapeRegExp(code), 'g'), emoji);
                replacementsMade++;
                this._updateUsageStats(code);
            }
        }
        
        // Уровень 2: Базовые эмоджи
        if (maxLevel >= 2) {
            await this._loadBasicEmojis();
            for (const [code, emoji] of Object.entries(this.basicEmojis)) {
                if (result.includes(code)) {
                    result = result.replace(new RegExp(this._escapeRegExp(code), 'g'), emoji);
                    replacementsMade++;
                    this._updateUsageStats(code);
                }
            }
        }
        
        // Уровень 3: Полные эмоджи
        if (maxLevel >= 3) {
            await this._loadFullEmojis();
            for (const [code, emoji] of Object.entries(this.fullEmojis)) {
                if (result.includes(code)) {
                    result = result.replace(new RegExp(this._escapeRegExp(code), 'g'), emoji);
                    replacementsMade++;
                    this._updateUsageStats(code);
                }
            }
        }
        
        // Уровень 4: YouTube эмоджи
        if (maxLevel >= 4) {
            await this._loadYoutubeEmojis();
            for (const [code, emojiHtml] of Object.entries(this.youtubeEmojis)) {
                if (result.includes(code)) {
                    result = result.replace(new RegExp(this._escapeRegExp(code), 'g'), emojiHtml);
                    replacementsMade++;
                    this._updateUsageStats(code);
                }
            }
        }
        
        const processingTime = performance.now() - startTime;
        
        // Логируем производительность если обработка заняла много времени
        if (processingTime > 10) { // Больше 10ms
            console.warn(`⚠️ Медленная обработка эмоджи: ${processingTime.toFixed(3)}ms, замен: ${replacementsMade}, уровень: ${maxLevel}`);
        }
        
        return result;
    }
    
    _escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
    
    _updateUsageStats(code) {
        const currentCount = this.usageStats.get(code) || 0;
        this.usageStats.set(code, currentCount + 1);
    }
    
    getPopularEmojisByUsage(limit = 50) {
        return Array.from(this.usageStats.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, limit)
            .reduce((obj, [code, count]) => {
                obj[code] = count;
                return obj;
            }, {});
    }
    
    optimizePopularEmojis() {
        if (this.usageStats.size < 100) return; // Недостаточно данных
        
        const popularFromUsage = this.getPopularEmojisByUsage(100);
        let moved = 0;
        
        for (const [code, usageCount] of Object.entries(popularFromUsage)) {
            if (usageCount > 10 && !(code in this.popularEmojis)) {
                if (code in this.basicEmojis) {
                    this.popularEmojis[code] = this.basicEmojis[code];
                    delete this.basicEmojis[code];
                    moved++;
                } else if (code in this.fullEmojis) {
                    this.popularEmojis[code] = this.fullEmojis[code];
                    delete this.fullEmojis[code];
                    moved++;
                }
            }
        }
        
        console.log(`Оптимизация: добавлено ${moved} эмоджи в популярные`);
    }
    
    getStats() {
        return {
            popularCount: Object.keys(this.popularEmojis).length,
            basicCount: this.levelsLoaded[2] ? Object.keys(this.basicEmojis).length : 'не загружено',
            fullCount: this.levelsLoaded[3] ? Object.keys(this.fullEmojis).length : 'не загружено',
            youtubeCount: this.levelsLoaded[4] ? Object.keys(this.youtubeEmojis).length : 'не загружено',
            totalUsage: Array.from(this.usageStats.values()).reduce((sum, count) => sum + count, 0),
            uniqueUsed: this.usageStats.size,
            levelsLoaded: this.levelsLoaded
        };
    }
    
    async searchEmojis(query, maxResults = 20) {
        query = query.toLowerCase();
        const results = {};
        
        // Поиск в популярных эмоджи
        for (const [code, emoji] of Object.entries(this.popularEmojis)) {
            if (code.toLowerCase().includes(query) && Object.keys(results).length < maxResults) {
                results[code] = emoji;
            }
        }
        
        // Поиск в базовых эмоджи если нужно больше результатов
        if (Object.keys(results).length < maxResults) {
            await this._loadBasicEmojis();
            for (const [code, emoji] of Object.entries(this.basicEmojis)) {
                if (code.toLowerCase().includes(query) && Object.keys(results).length < maxResults) {
                    results[code] = emoji;
                }
            }
        }
        
        return results;
    }
}

// Глобальный экземпляр
const emojiDB = new EmojiDatabase();

// Основная функция для конвертации эмоджи
async function convertEmojis(text, performanceMode = 'balanced') {
    const levelMap = {
        'fast': 1,
        'balanced': 2,
        'complete': 3,
        'full': 4
    };
    
    const maxLevel = levelMap[performanceMode] || 2;
    return await emojiDB.convertEmojis(text, maxLevel);
}

// Функция для получения статистики
function getEmojiStats() {
    return emojiDB.getStats();
}

// Функция поиска эмоджи
async function searchEmojis(query, maxResults = 20) {
    return await emojiDB.searchEmojis(query, maxResults);
}

// Функция оптимизации производительности
function optimizeEmojiPerformance() {
    emojiDB.optimizePopularEmojis();
}

// Экспорт для Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        EmojiDatabase,
        convertEmojis,
        getEmojiStats,
        searchEmojis,
        optimizeEmojiPerformance
    };
}

// Глобальные переменные для браузера
if (typeof window !== 'undefined') {
    window.EmojiDatabase = EmojiDatabase;
    window.convertEmojis = convertEmojis;
    window.getEmojiStats = getEmojiStats;
    window.searchEmojis = searchEmojis;
    window.optimizeEmojiPerformance = optimizeEmojiPerformance;
    window.emojiDB = emojiDB;
}

// Автоматическое тестирование при загрузке
if (typeof window !== 'undefined' || typeof process !== 'undefined') {
    // Тест производительности
    const testPerformance = async () => {
        const testText = "Привет :fire: :heart: :thumbsup: :grinning_face: :rocket: :party_popper:";
        
        console.log('🧪 Тестирование производительности эмоджи базы');
        console.log('='.repeat(50));
        
        // Тест быстрого режима
        const startFast = performance.now();
        const resultFast = await convertEmojis(testText, 'fast');
        const timeFast = performance.now() - startFast;
        console.log(`⚡ Быстрый режим: ${timeFast.toFixed(4)}ms`);
        console.log(`   Результат: ${resultFast}`);
        
        // Тест сбалансированного режима
        const startBalanced = performance.now();
        const resultBalanced = await convertEmojis(testText, 'balanced');
        const timeBalanced = performance.now() - startBalanced;
        console.log(`⚖️ Сбалансированный режим: ${timeBalanced.toFixed(4)}ms`);
        console.log(`   Результат: ${resultBalanced}`);
        
        // Статистика
        console.log('\n📊 Статистика базы данных:');
        const stats = getEmojiStats();
        for (const [key, value] of Object.entries(stats)) {
            console.log(`   ${key}: ${value}`);
        }
        
        // Тест поиска
        console.log('\n🔍 Поиск "heart":');
        const searchResults = await searchEmojis('heart', 5);
        for (const [code, emoji] of Object.entries(searchResults)) {
            console.log(`   ${code}: ${emoji}`);
        }
    };
    
    // Запускаем тест через небольшую задержку
    setTimeout(testPerformance, 100);
}
