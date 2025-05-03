from typing import Optional, Dict, Any
import asyncpg

from repositories.postgres_repository import PostgresRepository


class ClubRepository(PostgresRepository):
    def __init__(self, pool: asyncpg.Pool):
        super().__init__(pool, 'clubs')

    async def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find a club by name (case insensitive, partial match)"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow('SELECT * FROM clubs WHERE name ILIKE $1', f'{name}%')
