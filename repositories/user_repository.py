from typing import Optional, Dict, Any
import asyncpg

from repositories.postgres_repository import PostgresRepository


class UserRepository(PostgresRepository):
    def __init__(self, pool: asyncpg.Pool):
        super().__init__(pool, 'users')

    async def find_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Find a user by Telegram ID"""
        return await self.find_by('telegram_id', telegram_id)

    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find a user by email (case insensitive)"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow('SELECT * FROM users WHERE LOWER(email) = $1', email.lower())
