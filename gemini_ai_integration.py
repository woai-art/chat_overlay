#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Интеграция с Gemini AI для интерактивных функций LiveChat
"""

import google.generativeai as genai
import json
import time
import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import os
from dataclasses import dataclass

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Структура сообщения чата"""
    author: str
    text: str
    timestamp: int
    is_moderator: bool = False
    is_sponsor: bool = False
    is_owner: bool = False

@dataclass
class PollResult:
    """Результат опроса"""
    question: str
    options: List[str]
    duration_minutes: int
    category: str

@dataclass
class ContestEntry:
    """Участие в конкурсе"""
    author: str
    content: str
    timestamp: int
    score: float = 0.0

class RateLimiter:
    """Ограничитель запросов для соблюдения лимитов API"""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def can_make_request(self) -> bool:
        """Проверяет, можно ли сделать запрос"""
        now = time.time()
        # Удаляем старые запросы
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        return len(self.requests) < self.max_requests
    
    def add_request(self):
        """Регистрирует новый запрос"""
        self.requests.append(time.time())

class GeminiChatAI:
    """Основной класс для работы с Gemini AI"""
    
    def __init__(self, api_key: str):
        """
        Инициализация Gemini AI
        
        Args:
            api_key: API ключ для Gemini
        """
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            
            # Ограничители запросов (бесплатный тариф)
            self.rate_limiter = RateLimiter(15, 60)  # 15 запросов в минуту
            self.daily_limiter = RateLimiter(1500, 86400)  # 1500 запросов в день
            
            logger.info("✅ Gemini AI инициализирован успешно")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Gemini AI: {e}")
            raise
    
    def _can_make_request(self) -> bool:
        """Проверяет лимиты API"""
        return self.rate_limiter.can_make_request() and self.daily_limiter.can_make_request()
    
    def _register_request(self):
        """Регистрирует выполненный запрос"""
        self.rate_limiter.add_request()
        self.daily_limiter.add_request()
    
    async def _make_request(self, prompt: str) -> Optional[str]:
        """Безопасный запрос к Gemini API с обработкой лимитов"""
        
        if not self._can_make_request():
            logger.warning("⚠️ Достигнут лимит запросов к Gemini API")
            return None
        
        try:
            response = self.model.generate_content(prompt)
            self._register_request()
            
            if response.text:
                logger.info(f"✅ Успешный запрос к Gemini AI (длина ответа: {len(response.text)})")
                return response.text
            else:
                logger.warning("⚠️ Gemini вернул пустой ответ")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка запроса к Gemini API: {e}")
            return None
    
    async def analyze_chat_sentiment(self, messages: List[ChatMessage]) -> Optional[Dict]:
        """
        Анализирует настроение в чате
        
        Args:
            messages: Список последних сообщений
            
        Returns:
            Словарь с анализом настроения или None при ошибке
        """
        
        if not messages:
            return None
        
        # Подготавливаем данные для анализа
        chat_text = "\n".join([f"{msg.author}: {msg.text}" for msg in messages[-20:]])  # Последние 20 сообщений
        
        prompt = f"""
        Проанализируй настроение в чате на основе последних сообщений:
        
        {chat_text}
        
        Верни результат ТОЛЬКО в формате JSON без дополнительного текста:
        {{
            "overall_mood": "позитивное|нейтральное|негативное",
            "energy_level": "высокий|средний|низкий",
            "main_topics": ["тема1", "тема2", "тема3"],
            "activity_level": "активный|умеренный|тихий",
            "suggestions_for_streamer": ["совет1", "совет2"],
            "interesting_questions": ["вопрос1", "вопрос2"]
        }}
        """
        
        response = await self._make_request(prompt)
        if not response:
            return None
        
        try:
            # Извлекаем JSON из ответа
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_text = response[json_start:json_end]
                result = json.loads(json_text)
                logger.info(f"📊 Анализ настроения: {result['overall_mood']}, активность: {result['activity_level']}")
                return result
            else:
                logger.error("❌ Не удалось извлечь JSON из ответа Gemini")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Ошибка парсинга JSON ответа: {e}")
            return None
    
    async def create_smart_poll(self, context: str, recent_messages: List[ChatMessage]) -> Optional[PollResult]:
        """
        Создает умный опрос на основе контекста стрима
        
        Args:
            context: Контекст стрима (тема, что происходит)
            recent_messages: Последние сообщения для анализа
            
        Returns:
            PollResult или None при ошибке
        """
        
        chat_context = "\n".join([f"{msg.author}: {msg.text}" for msg in recent_messages[-15:]])
        
        prompt = f"""
        Создай интересный опрос для зрителей стрима.
        
        Контекст стрима: {context}
        Последние сообщения чата:
        {chat_context}
        
        Создай опрос, который будет интересен зрителям и связан с происходящим.
        
        Верни результат ТОЛЬКО в формате JSON:
        {{
            "question": "Текст вопроса (максимум 100 символов)",
            "options": ["вариант1", "вариант2", "вариант3", "вариант4"],
            "duration_minutes": 3,
            "category": "развлечение|обучение|игра|общение"
        }}
        """
        
        response = await self._make_request(prompt)
        if not response:
            return None
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_text = response[json_start:json_end]
                data = json.loads(json_text)
                
                poll = PollResult(
                    question=data['question'],
                    options=data['options'],
                    duration_minutes=data['duration_minutes'],
                    category=data['category']
                )
                
                logger.info(f"📊 Создан опрос: {poll.question}")
                return poll
            else:
                return None
                
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"❌ Ошибка создания опроса: {e}")
            return None
    
    async def evaluate_contest_entries(self, entries: List[ContestEntry], contest_type: str) -> List[ContestEntry]:
        """
        Оценивает участников конкурса
        
        Args:
            entries: Список участников конкурса
            contest_type: Тип конкурса (лучший_вопрос, креативность, активность)
            
        Returns:
            Отсортированный список участников с оценками
        """
        
        if not entries:
            return []
        
        entries_text = "\n".join([f"{i+1}. {entry.author}: {entry.content}" for i, entry in enumerate(entries)])
        
        criteria_map = {
            "лучший_вопрос": "оригинальность, релевантность, интересность для стримера",
            "креативность": "творческий подход, оригинальность, юмор",
            "активность": "качество участия, позитивность, вовлеченность"
        }
        
        criteria = criteria_map.get(contest_type, "общее качество")
        
        prompt = f"""
        Оцени участников конкурса "{contest_type}" по критериям: {criteria}
        
        Участники:
        {entries_text}
        
        Верни результат ТОЛЬКО в формате JSON:
        {{
            "rankings": [
                {{"position": 1, "author": "имя", "score": 9.5, "reason": "краткое обоснование"}},
                {{"position": 2, "author": "имя", "score": 8.7, "reason": "краткое обоснование"}}
            ]
        }}
        
        Оценки от 1 до 10. Учитывай: {criteria}
        """
        
        response = await self._make_request(prompt)
        if not response:
            return entries
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_text = response[json_start:json_end]
                data = json.loads(json_text)
                
                # Применяем оценки
                rankings = {item['author']: item['score'] for item in data['rankings']}
                
                for entry in entries:
                    if entry.author in rankings:
                        entry.score = rankings[entry.author]
                
                # Сортируем по оценке
                entries.sort(key=lambda x: x.score, reverse=True)
                
                logger.info(f"🏆 Оценены {len(entries)} участников конкурса '{contest_type}'")
                return entries
                
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"❌ Ошибка оценки конкурса: {e}")
        
        return entries
    
    async def generate_conversation_starter(self, chat_analysis: Dict) -> Optional[str]:
        """
        Генерирует предложение для стримера на основе анализа чата
        
        Args:
            chat_analysis: Результат анализа настроения чата
            
        Returns:
            Предложение для стримера или None
        """
        
        prompt = f"""
        На основе анализа чата предложи стримеру интересную тему для обсуждения или активность.
        
        Анализ чата:
        - Настроение: {chat_analysis.get('overall_mood', 'неизвестно')}
        - Энергия: {chat_analysis.get('energy_level', 'неизвестно')}
        - Основные темы: {', '.join(chat_analysis.get('main_topics', []))}
        - Активность: {chat_analysis.get('activity_level', 'неизвестно')}
        
        Предложи ОДНО конкретное действие для стримера (максимум 150 символов).
        Примеры: "Спросите зрителей о...", "Проведите опрос про...", "Расскажите о..."
        
        Верни только текст предложения без дополнительного форматирования.
        """
        
        response = await self._make_request(prompt)
        if response:
            # Очищаем ответ от лишнего форматирования
            suggestion = response.strip().replace('"', '').replace('*', '')
            logger.info(f"💡 Предложение для стримера: {suggestion[:50]}...")
            return suggestion
        
        return None

class InteractiveManager:
    """Менеджер интерактивных функций"""
    
    def __init__(self, gemini_ai: GeminiChatAI):
        self.ai = gemini_ai
        self.active_polls = {}
        self.active_contests = {}
        self.user_stats = {}
        self.last_analysis_time = 0
        self.analysis_interval = 300  # 5 минут между анализами
    
    async def process_chat_messages(self, messages: List[ChatMessage]) -> Dict:
        """
        Обрабатывает сообщения чата и возвращает рекомендации
        
        Args:
            messages: Список сообщений для обработки
            
        Returns:
            Словарь с рекомендациями и анализом
        """
        
        current_time = time.time()
        
        # Анализируем чат не чаще раза в 5 минут
        if current_time - self.last_analysis_time < self.analysis_interval:
            return {"status": "waiting", "next_analysis_in": self.analysis_interval - (current_time - self.last_analysis_time)}
        
        # Анализируем настроение
        sentiment = await self.ai.analyze_chat_sentiment(messages)
        if not sentiment:
            return {"status": "error", "message": "Не удалось проанализировать чат"}
        
        # Генерируем предложение для стримера
        suggestion = await self.ai.generate_conversation_starter(sentiment)
        
        self.last_analysis_time = current_time
        
        result = {
            "status": "success",
            "analysis": sentiment,
            "suggestion": suggestion,
            "timestamp": current_time
        }
        
        logger.info(f"📊 Анализ чата завершен: настроение {sentiment['overall_mood']}")
        return result
    
    async def create_auto_poll(self, context: str, messages: List[ChatMessage]) -> Optional[PollResult]:
        """Создает автоматический опрос"""
        
        poll = await self.ai.create_smart_poll(context, messages)
        if poll:
            poll_id = f"poll_{int(time.time())}"
            self.active_polls[poll_id] = {
                "poll": poll,
                "start_time": time.time(),
                "votes": {}
            }
            logger.info(f"📊 Запущен опрос: {poll.question}")
        
        return poll
    
    def get_api_status(self) -> Dict:
        """Возвращает статус API и лимитов"""
        
        return {
            "rate_limit_ok": self.ai.rate_limiter.can_make_request(),
            "daily_limit_ok": self.ai.daily_limiter.can_make_request(),
            "requests_this_minute": len(self.ai.rate_limiter.requests),
            "requests_today": len(self.ai.daily_limiter.requests)
        }

def load_api_key() -> Optional[str]:
    """Загружает API ключ из файла или переменной окружения"""
    
    # Пробуем загрузить из файла
    if os.path.exists('gemini_api_key.txt'):
        try:
            with open('gemini_api_key.txt', 'r') as f:
                key = f.read().strip()
                if key:
                    logger.info("✅ API ключ загружен из файла")
                    return key
        except Exception as e:
            logger.error(f"❌ Ошибка чтения файла с ключом: {e}")
    
    # Пробуем загрузить из переменной окружения
    key = os.getenv('GEMINI_API_KEY')
    if key:
        logger.info("✅ API ключ загружен из переменной окружения")
        return key
    
    logger.warning("⚠️ API ключ не найден. Создайте файл gemini_api_key.txt или установите переменную GEMINI_API_KEY")
    return None

# Пример использования
async def main():
    """Пример использования системы"""
    
    api_key = load_api_key()
    if not api_key:
        print("❌ Не найден API ключ Gemini")
        return
    
    try:
        # Инициализируем ИИ
        ai = GeminiChatAI(api_key)
        manager = InteractiveManager(ai)
        
        # Тестовые сообщения
        test_messages = [
            ChatMessage("User1", "Привет! Как дела?", int(time.time())),
            ChatMessage("User2", "Отличный стрим!", int(time.time())),
            ChatMessage("User3", "Можно вопрос про игру?", int(time.time())),
        ]
        
        # Анализируем чат
        result = await manager.process_chat_messages(test_messages)
        print(f"📊 Результат анализа: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        # Создаем опрос
        poll = await manager.create_auto_poll("Игровой стрим", test_messages)
        if poll:
            print(f"📊 Создан опрос: {poll.question}")
            print(f"   Варианты: {', '.join(poll.options)}")
        
        # Статус API
        status = manager.get_api_status()
        print(f"🔧 Статус API: {json.dumps(status, indent=2)}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в main: {e}")

if __name__ == "__main__":
    asyncio.run(main())
