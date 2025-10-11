from typing import Optional, Dict, Any, List
import asyncpg

from repositories.postgres_repository import PostgresRepository


class CountryRepository(PostgresRepository):
    def __init__(self, pool: asyncpg.Pool):
        super().__init__(pool, 'countries')

    async def find_all(self) -> List[Dict[str, Any]]:
        """Find all countries ordered by code"""
        async with self.pool.acquire() as conn:
            return await conn.fetch('SELECT * FROM countries ORDER BY id')

    async def find_by_id(self, country_id: int) -> Optional[Dict[str, Any]]:
        """Find a country by ID"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow('SELECT * FROM countries WHERE id = $1', country_id)
