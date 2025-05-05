from app import logger
from typing import Any, Dict, Optional
from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

class BaseSecurityMiddleware(BaseMiddleware):
    """Базовый класс для middleware безопасности"""
    
    def __init__(self, security_instance: Any):
        self.security = security_instance
        super().__init__()
    
    async def on_process_message(self, message: types.Message, data: Dict[str, Any]):
        """Обработка входящего сообщения"""
        try:
            result = self.security.check_message(message)
            if isinstance(result, tuple):
                is_allowed, warning = result
                if warning:
                    await message.answer(warning)
                if not is_allowed:
                    raise CancelHandler()
            elif not result:
                raise CancelHandler()
        except Exception as e:
            logger.error(f"Ошибка в middleware {self.__class__.__name__}: {e}")
            raise CancelHandler() 