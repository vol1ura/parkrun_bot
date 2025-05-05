import re
from typing import Any, Dict, Optional, Tuple
from aiogram import types

from .base_middleware import BaseSecurityMiddleware
from app import logger

class InfernaselFastsec:
    def __init__(self):
        # Паттерны для обнаружения атак
        self.patterns = {
            'sql': [
                r'(?i)(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|WHERE|FROM|JOIN)',
                r'(?i)(--|#|/\*|\*/)',
                r'(?i)(OR\s+1=1|AND\s+1=1)',
                r'(?i)(EXEC\s+\(|EXECUTE\s+\()',
                r'(?i)(WAITFOR\s+DELAY|SLEEP\s+\()',
                r'(?i)(UNION\s+ALL\s+SELECT)',
                r'(?i)(INTO\s+OUTFILE|INTO\s+DUMPFILE)',
                r'(?i)(LOAD_FILE|LOAD_DATA)',
                r'(?i)(BENCHMARK|SLEEP)',
                r'(?i)(PG_SLEEP|WAITFOR)'
            ],
            'xss': [
                r'<script.*?>.*?</script>',
                r'javascript:',
                r'on\w+\s*=',
                r'<.*?on\w+\s*=',
                r'<.*?src=.*?>',
                r'<.*?href=.*?>',
                r'<.*?style=.*?>',
                r'<.*?iframe.*?>',
                r'<.*?img.*?>',
                r'<.*?svg.*?>'
            ],
            'command': [
                r'(?i)(cmd\.exe|/bin/sh|/bin/bash)',
                r'(?i)(system\(|exec\(|shell_exec\()',
                r'(?i)(&&|\|\||;)',
                r'(?i)(\$\{.*?\})',
                r'(?i)(\$\$|\$\(.*?\))'
            ]
        }
        
        # Сообщения для разных типов атак
        self.warning_messages = {
            'sql': {
                'text': "⚠️ Обнаружена попытка SQL-инъекции. Это может быть опасно для безопасности данных.",
                'caption': "⚠️ В подписи к файлу обнаружена попытка SQL-инъекции."
            },
            'xss': {
                'text': "⚠️ Обнаружена попытка XSS-атаки. Пожалуйста, не используйте вредоносный код.",
                'caption': "⚠️ В подписи к файлу обнаружена попытка XSS-атаки."
            },
            'command': {
                'text': "⚠️ Обнаружена попытка командной инъекции. Это может быть опасно для сервера.",
                'caption': "⚠️ В подписи к файлу обнаружена попытка командной инъекции."
            }
        }
        
        # Список подозрительных IP-адресов
        self.suspicious_ips: Dict[str, int] = {}
        
        # Максимальное количество попыток перед блокировкой
        self.max_attempts = 5
        
        # Время блокировки в секундах
        self.block_time = 3600

    def check_text(self, text: str, text_type: str = 'text') -> Optional[str]:
        """Проверка текста на различные типы атак"""
        if not text:
            return None
            
        for attack_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    logger.info(f"Обнаружена попытка {attack_type}-атаки: {text}")
                    return self.warning_messages[attack_type][text_type]
        return None

    def check_ip(self, ip: str) -> bool:
        """Проверка IP-адреса на подозрительную активность"""
        if ip in self.suspicious_ips:
            self.suspicious_ips[ip] += 1
            if self.suspicious_ips[ip] >= self.max_attempts:
                logger.warning(f"IP {ip} заблокирован за подозрительную активность")
                return True
        else:
            self.suspicious_ips[ip] = 1
        return False

    def sanitize_input(self, text: str) -> str:
        """Очистка входных данных"""
        return re.sub(r'<[^>]+>', '', text).replace("'", "''").replace('"', '""')

    def check_message(self, message: types.Message) -> Tuple[bool, Optional[str]]:
        """Проверка сообщения на различные типы атак"""
        warning = None
        
        # Получаем IP-адрес пользователя
        ip = message.from_user.id  # В реальном приложении нужно получать реальный IP
        
        # Проверяем IP
        if self.check_ip(ip):
            return False, warning
        
        # Проверяем текст сообщения
        if message.text:
            warning = self.check_text(message.text)
        
        # Проверяем caption для медиафайлов
        if not warning and message.caption:
            warning = self.check_text(message.caption, 'caption')
        
        return True, warning

class SecurityMiddleware(BaseSecurityMiddleware):
    """Middleware для защиты от атак"""
    pass 