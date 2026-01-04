#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка наличия YouTube cookies в разных браузерах
"""

import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def check_browser_cookies():
    """Проверяет наличие YouTube cookies во всех браузерах"""
    try:
        import browser_cookie3
        
        browsers = {
            'Chrome': browser_cookie3.chrome,
            'Edge': browser_cookie3.edge,
            'Firefox': browser_cookie3.firefox,
            'Opera': browser_cookie3.opera,
            'Chromium': browser_cookie3.chromium,
        }
        
        logger.info("=" * 60)
        logger.info("Проверка YouTube cookies в браузерах")
        logger.info("=" * 60)
        logger.info("")
        
        found_browsers = []
        
        for browser_name, browser_func in browsers.items():
            try:
                logger.info(f"🔍 Проверка {browser_name}...")
                cookies = list(browser_func(domain_name='youtube.com'))
                
                if cookies:
                    # Проверяем наличие важных cookies для авторизации
                    cookie_names = [c.name for c in cookies]
                    has_auth = any(name in cookie_names for name in ['SAPISID', 'SSID', '__Secure-3PAPISID'])
                    
                    logger.info(f"  ✅ Найдено {len(cookies)} cookies")
                    if has_auth:
                        logger.info(f"  ✅ Найдены cookies авторизации!")
                        found_browsers.append((browser_name, len(cookies), True))
                    else:
                        logger.info(f"  ⚠️  Cookies есть, но нет данных авторизации")
                        found_browsers.append((browser_name, len(cookies), False))
                else:
                    logger.info(f"  ❌ Cookies не найдены")
                    
            except Exception as e:
                logger.info(f"  ❌ Ошибка: {e}")
            
            logger.info("")
        
        logger.info("=" * 60)
        
        if found_browsers:
            logger.info("📊 Результаты:")
            logger.info("")
            for browser, count, has_auth in found_browsers:
                status = "✅ АВТОРИЗОВАН" if has_auth else "⚠️  БЕЗ АВТОРИЗАЦИИ"
                logger.info(f"  {browser}: {count} cookies - {status}")
            
            # Находим лучший браузер
            auth_browsers = [b for b in found_browsers if b[2]]
            if auth_browsers:
                best = max(auth_browsers, key=lambda x: x[1])
                logger.info("")
                logger.info(f"🎯 Рекомендуется использовать: {best[0]}")
                return best[0].lower()
        else:
            logger.info("❌ Не найдено YouTube cookies ни в одном браузере")
            logger.info("")
            logger.info("Возможные причины:")
            logger.info("1. Вы не вошли в YouTube ни в одном браузере")
            logger.info("2. Все браузеры сейчас открыты (закройте их)")
            logger.info("3. Браузер хранит cookies в нестандартном месте")
        
        return None
        
    except ImportError:
        logger.error("❌ Библиотека browser_cookie3 не установлена")
        return None
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    try:
        best_browser = check_browser_cookies()
        
        if best_browser:
            logger.info("")
            logger.info("=" * 60)
            logger.info(f"Для извлечения cookies из {best_browser.capitalize()}, запустите:")
            logger.info(f"  python extract_youtube_cookies_from_{best_browser}.py")
            logger.info("=" * 60)
        
        input("\nНажмите Enter для выхода...")
        
    except KeyboardInterrupt:
        logger.info("\n\nПрервано пользователем")
    except Exception as e:
        logger.error(f"\n\n❌ Ошибка: {e}")
        input("\nНажмите Enter для выхода...")

