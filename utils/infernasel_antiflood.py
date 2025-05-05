from app import logger
from typing import Dict, Any, Set
from datetime import datetime, timedelta
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler

from .base_middleware import BaseSecurityMiddleware

class InfernaselAntiflood:
    def __init__(self, 
                 message_limit: int = 5,
                 time_window: int = 60,
                 max_file_size: int = 20 * 1024 * 1024,  # 20MB
                 supported_types: Set[str] = None):
        self.message_limit = message_limit
        self.time_window = time_window
        self.max_file_size = max_file_size
        self.supported_types = supported_types or {
            'text', 'photo', 'document', 'audio', 'video', 'voice', 'sticker'
        }
        self.user_messages: Dict[int, list] = {}

    def check_message(self, message: types.Message) -> bool:
        """Проверка сообщения на флуд и поддерживаемые типы"""
        user_id = message.from_user.id
        message_type = message.content_type
        
        # Проверка типа сообщения
        if message_type not in self.supported_types:
            logger.info(f"Игнорируем неподдерживаемый тип сообщения от {user_id}: {message_type}")
            return False

        # Проверка размера файла
        if message_type in {'document', 'photo', 'audio', 'video'}:
            file_size = getattr(message, message_type).file_size
            if file_size > self.max_file_size:
                logger.info(f"Игнорируем слишком большой файл от {user_id}: {file_size} байт")
                return False

        # Проверка на флуд
        now = datetime.now()
        if user_id not in self.user_messages:
            self.user_messages[user_id] = []
        
        # Удаляем старые сообщения и добавляем новое
        self.user_messages[user_id] = [
            msg_time for msg_time in self.user_messages[user_id]
            if now - msg_time < timedelta(seconds=self.time_window)
        ] + [now]
        
        # Проверяем лимит
        if len(self.user_messages[user_id]) > self.message_limit:
            logger.info(f"Игнорируем сообщение от {user_id} из-за превышения лимита")
            return False
        
        return True

class AntifloodMiddleware(BaseSecurityMiddleware):
    """Middleware для защиты от флуда"""
    pass 