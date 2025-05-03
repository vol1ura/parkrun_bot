import asyncio
import logging
import signal
import sys
from typing import Callable, Any
import psutil
import gc

logger = logging.getLogger(__name__)

class InfernaselAnticrash:
    def __init__(self, max_memory_percent: int = 80, max_cpu_percent: int = 90):
        self.max_memory_percent = max_memory_percent
        self.max_cpu_percent = max_cpu_percent
        self.original_signal_handlers = {}
        self.cleanup_tasks = []

    async def monitor_resources(self):
        """Мониторинг использования ресурсов"""
        while True:
            try:
                memory_percent = psutil.Process().memory_percent()
                cpu_percent = psutil.Process().cpu_percent()
                
                if memory_percent > self.max_memory_percent:
                    logger.warning(f"Высокое использование памяти: {memory_percent}%")
                    await self.cleanup_memory()
                
                if cpu_percent > self.max_cpu_percent:
                    logger.warning(f"Высокая нагрузка на CPU: {cpu_percent}%")
                    await self.reduce_cpu_load()
                
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Ошибка мониторинга ресурсов: {e}")

    async def cleanup_memory(self):
        """Очистка памяти"""
        try:
            gc.collect()
            logger.info("Выполнена очистка памяти")
        except Exception as e:
            logger.error(f"Ошибка очистки памяти: {e}")

    async def reduce_cpu_load(self):
        """Снижение нагрузки на CPU"""
        try:
            await asyncio.sleep(1)  # Даем процессору передышку
            logger.info("Выполнено снижение нагрузки на CPU")
        except Exception as e:
            logger.error(f"Ошибка снижения нагрузки на CPU: {e}")

    def register_cleanup_task(self, task: Callable):
        """Регистрация задачи очистки"""
        self.cleanup_tasks.append(task)

    async def graceful_shutdown(self, signum: int, frame: Any):
        """Грациозное завершение работы"""
        logger.info(f"Получен сигнал {signum}, начинаем завершение работы...")
        
        # Выполняем зарегистрированные задачи очистки
        for task in self.cleanup_tasks:
            try:
                await task()
            except Exception as e:
                logger.error(f"Ошибка при выполнении задачи очистки: {e}")
        
        # Восстанавливаем оригинальные обработчики сигналов
        for sig, handler in self.original_signal_handlers.items():
            signal.signal(sig, handler)
        
        sys.exit(0)

    def setup(self):
        """Настройка антикрэш системы"""
        # Сохраняем оригинальные обработчики сигналов
        for sig in (signal.SIGINT, signal.SIGTERM):
            self.original_signal_handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, lambda s, f: asyncio.create_task(self.graceful_shutdown(s, f)))
        
        # Запускаем мониторинг ресурсов
        asyncio.create_task(self.monitor_resources())
        
        logger.info("Infernasel Anticrash система активирована") 