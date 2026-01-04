#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Интеграция ИИ функций с существующей системой LiveChat
"""

import json
import time
import asyncio
import threading
from typing import List, Dict, Optional
import logging
from datetime import datetime
from gemini_ai_integration import GeminiChatAI, InteractiveManager, ChatMessage, load_api_key

logger = logging.getLogger(__name__)

class AIChatBridge:
    """Мост между ИИ системой и LiveChat"""
    
    def __init__(self):
        self.ai_manager = None
        self.is_running = False
        self.last_messages = []
        self.analysis_results = {}
        self.active_polls = {}
        self.active_contests = {}
        
        # Настройки
        self.settings = {
            'ai_enabled': False,
            'auto_analysis_interval': 300,  # 5 минут
            'auto_polls_enabled': False,
            'auto_contests_enabled': False,
            'stream_context': 'Игровой стрим'
        }
        
        self.load_ai_settings()
    
    def load_ai_settings(self):
        """Загружает настройки ИИ"""
        try:
            with open('ai_settings.json', 'r', encoding='utf-8') as f:
                saved_settings = json.load(f)
                self.settings.update(saved_settings)
                logger.info("✅ Настройки ИИ загружены")
        except FileNotFoundError:
            logger.info("📝 Создаю файл настроек ИИ по умолчанию")
            self.save_ai_settings()
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки настроек ИИ: {e}")
    
    def save_ai_settings(self):
        """Сохраняет настройки ИИ"""
        try:
            with open('ai_settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
                logger.info("💾 Настройки ИИ сохранены")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения настроек ИИ: {e}")
    
    async def initialize_ai(self) -> bool:
        """Инициализирует ИИ систему"""
        
        api_key = load_api_key()
        if not api_key:
            logger.error("❌ Не найден API ключ Gemini")
            return False
        
        try:
            ai = GeminiChatAI(api_key)
            self.ai_manager = InteractiveManager(ai)
            self.settings['ai_enabled'] = True
            self.save_ai_settings()
            
            logger.info("🤖 ИИ система инициализирована успешно")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации ИИ: {e}")
            return False
    
    def read_chat_messages(self) -> List[ChatMessage]:
        """Читает сообщения из messages.json"""
        
        try:
            with open('messages.json', 'r', encoding='utf-8') as f:
                messages_data = json.load(f)
            
            # Конвертируем в ChatMessage объекты
            chat_messages = []
            for msg_data in messages_data[-50:]:  # Последние 50 сообщений
                try:
                    author = msg_data['author']
                    
                    chat_msg = ChatMessage(
                        author=author.get('display_name', author.get('name', 'Unknown')),
                        text=msg_data['text'],
                        timestamp=msg_data['timestamp'],
                        is_moderator=author.get('is_moderator', False),
                        is_sponsor=author.get('is_sponsor', False),
                        is_owner=author.get('is_owner', False)
                    )
                    
                    chat_messages.append(chat_msg)
                    
                except KeyError as e:
                    logger.warning(f"⚠️ Пропущено сообщение с неполными данными: {e}")
                    continue
            
            return chat_messages
            
        except FileNotFoundError:
            logger.warning("⚠️ Файл messages.json не найден")
            return []
        except json.JSONDecodeError:
            logger.error("❌ Ошибка чтения messages.json")
            return []
        except Exception as e:
            logger.error(f"❌ Ошибка чтения сообщений: {e}")
            return []
    
    async def analyze_chat_auto(self):
        """Автоматический анализ чата"""
        
        if not self.ai_manager or not self.settings['ai_enabled']:
            return
        
        messages = self.read_chat_messages()
        if not messages:
            return
        
        # Проверяем, есть ли новые сообщения
        if messages == self.last_messages:
            return
        
        self.last_messages = messages
        
        try:
            # Анализируем чат
            result = await self.ai_manager.process_chat_messages(messages)
            
            if result.get('status') == 'success':
                self.analysis_results = result
                self.save_analysis_results()
                
                logger.info(f"📊 Автоанализ: настроение {result['analysis']['overall_mood']}")
                
                # Автоматически создаем опрос если включено
                if self.settings.get('auto_polls_enabled', False):
                    await self.create_auto_poll(messages)
                
        except Exception as e:
            logger.error(f"❌ Ошибка автоанализа: {e}")
    
    async def create_auto_poll(self, messages: List[ChatMessage]):
        """Создает автоматический опрос"""
        
        if not self.ai_manager:
            return
        
        try:
            poll = await self.ai_manager.create_auto_poll(
                self.settings['stream_context'], 
                messages
            )
            
            if poll:
                poll_id = f"poll_{int(time.time())}"
                self.active_polls[poll_id] = {
                    'poll': poll,
                    'start_time': time.time(),
                    'votes': {},
                    'status': 'active'
                }
                
                self.save_poll_data(poll_id, poll)
                logger.info(f"📊 Автоопрос создан: {poll.question}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания автоопроса: {e}")
    
    def save_analysis_results(self):
        """Сохраняет результаты анализа"""
        try:
            with open('ai_analysis.json', 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения анализа: {e}")
    
    def save_poll_data(self, poll_id: str, poll):
        """Сохраняет данные опроса"""
        try:
            poll_data = {
                'id': poll_id,
                'question': poll.question,
                'options': poll.options,
                'duration_minutes': poll.duration_minutes,
                'category': poll.category,
                'created_at': time.time(),
                'status': 'active'
            }
            
            # Сохраняем в файл для веб-интерфейса
            with open('current_poll.json', 'w', encoding='utf-8') as f:
                json.dump(poll_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"💾 Данные опроса сохранены: {poll_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения опроса: {e}")
    
    def get_ai_status(self) -> Dict:
        """Возвращает статус ИИ системы"""
        
        status = {
            'ai_enabled': self.settings['ai_enabled'],
            'ai_initialized': self.ai_manager is not None,
            'is_running': self.is_running,
            'last_analysis': self.analysis_results.get('timestamp', 0),
            'active_polls': len(self.active_polls),
            'active_contests': len(self.active_contests)
        }
        
        if self.ai_manager:
            api_status = self.ai_manager.get_api_status()
            status.update(api_status)
        
        return status
    
    async def manual_analysis(self) -> Optional[Dict]:
        """Ручной анализ чата"""
        
        if not self.ai_manager:
            return None
        
        messages = self.read_chat_messages()
        if not messages:
            return None
        
        try:
            result = await self.ai_manager.process_chat_messages(messages)
            
            if result.get('status') == 'success':
                self.analysis_results = result
                self.save_analysis_results()
                logger.info("📊 Ручной анализ чата завершен")
                return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка ручного анализа: {e}")
        
        return None
    
    async def create_manual_poll(self, context: str = None) -> Optional[Dict]:
        """Создает опрос вручную"""
        
        if not self.ai_manager:
            return None
        
        messages = self.read_chat_messages()
        context = context or self.settings['stream_context']
        
        try:
            poll = await self.ai_manager.create_auto_poll(context, messages)
            
            if poll:
                poll_id = f"poll_{int(time.time())}"
                self.active_polls[poll_id] = {
                    'poll': poll,
                    'start_time': time.time(),
                    'votes': {},
                    'status': 'active'
                }
                
                self.save_poll_data(poll_id, poll)
                
                return {
                    'id': poll_id,
                    'question': poll.question,
                    'options': poll.options,
                    'duration': poll.duration_minutes
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания опроса: {e}")
        
        return None
    
    async def start_auto_mode(self):
        """Запускает автоматический режим"""
        
        if not self.ai_manager:
            logger.error("❌ ИИ не инициализирован")
            return
        
        self.is_running = True
        logger.info("🚀 Автоматический режим ИИ запущен")
        
        while self.is_running:
            try:
                await self.analyze_chat_auto()
                await asyncio.sleep(self.settings['auto_analysis_interval'])
                
            except Exception as e:
                logger.error(f"❌ Ошибка в автоматическом режиме: {e}")
                await asyncio.sleep(60)  # Пауза при ошибке
    
    def stop_auto_mode(self):
        """Останавливает автоматический режим"""
        self.is_running = False
        logger.info("🛑 Автоматический режим ИИ остановлен")

class AIWebAPI:
    """Веб API для управления ИИ функциями"""
    
    def __init__(self, ai_bridge: AIChatBridge):
        self.bridge = ai_bridge
    
    async def handle_request(self, action: str, params: Dict = None) -> Dict:
        """Обрабатывает веб-запросы к ИИ"""
        
        params = params or {}
        
        try:
            if action == 'initialize':
                success = await self.bridge.initialize_ai()
                return {'success': success, 'message': 'ИИ инициализирован' if success else 'Ошибка инициализации'}
            
            elif action == 'status':
                return {'success': True, 'data': self.bridge.get_ai_status()}
            
            elif action == 'analyze':
                result = await self.bridge.manual_analysis()
                return {'success': result is not None, 'data': result}
            
            elif action == 'create_poll':
                context = params.get('context')
                poll = await self.bridge.create_manual_poll(context)
                return {'success': poll is not None, 'data': poll}
            
            elif action == 'start_auto':
                asyncio.create_task(self.bridge.start_auto_mode())
                return {'success': True, 'message': 'Автоматический режим запущен'}
            
            elif action == 'stop_auto':
                self.bridge.stop_auto_mode()
                return {'success': True, 'message': 'Автоматический режим остановлен'}
            
            elif action == 'settings':
                if 'update' in params:
                    self.bridge.settings.update(params['update'])
                    self.bridge.save_ai_settings()
                    return {'success': True, 'message': 'Настройки обновлены'}
                else:
                    return {'success': True, 'data': self.bridge.settings}
            
            else:
                return {'success': False, 'error': f'Неизвестное действие: {action}'}
                
        except Exception as e:
            logger.error(f"❌ Ошибка API запроса {action}: {e}")
            return {'success': False, 'error': str(e)}

# Глобальный экземпляр для использования в других модулях
ai_bridge = AIChatBridge()
ai_api = AIWebAPI(ai_bridge)

async def main():
    """Пример использования"""
    
    # Инициализируем ИИ
    success = await ai_bridge.initialize_ai()
    if not success:
        print("❌ Не удалось инициализировать ИИ")
        return
    
    # Анализируем чат
    result = await ai_bridge.manual_analysis()
    if result:
        print(f"📊 Анализ чата: {result['analysis']['overall_mood']}")
    
    # Создаем опрос
    poll = await ai_bridge.create_manual_poll("Игровой стрим")
    if poll:
        print(f"📊 Создан опрос: {poll['question']}")
    
    # Показываем статус
    status = ai_bridge.get_ai_status()
    print(f"🔧 Статус ИИ: {json.dumps(status, ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
