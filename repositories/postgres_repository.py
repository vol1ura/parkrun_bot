from typing import Any, Dict, List, Optional, TypeVar, Generic
import asyncpg

from repositories.base_repository import BaseRepository

T = TypeVar('T')


class PostgresRepository(BaseRepository[T], Generic[T]):
    def __init__(self, pool: asyncpg.Pool, table_name: str):
        self.pool = pool
        self.table_name = table_name

    async def find_by_id(self, id: Any) -> Optional[T]:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(f'SELECT * FROM {self.table_name} WHERE id = $1', id)

    async def find_by(self, field: str, value: Any) -> Optional[T]:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(f'SELECT * FROM {self.table_name} WHERE {field} = $1', value)

    async def find_all(self) -> List[T]:
        async with self.pool.acquire() as conn:
            return await conn.fetch(f'SELECT * FROM {self.table_name}')

    async def create(self, entity: Dict[str, Any]) -> T:
        fields = list(entity.keys())
        values = list(entity.values())

        placeholders = [f'${i+1}' for i in range(len(fields))]
        fields_str = ', '.join(fields)
        placeholders_str = ', '.join(placeholders)

        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                f'INSERT INTO {self.table_name} ({fields_str}) VALUES ({placeholders_str}) RETURNING *',
                *values
            )

    async def update(self, id: Any, entity: Dict[str, Any]) -> Optional[T]:
        fields = list(entity.keys())
        values = list(entity.values())

        set_clause = ', '.join([f'{field} = ${i+1}' for i, field in enumerate(fields)])

        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                f'UPDATE {self.table_name} SET {set_clause} WHERE id = ${len(fields)+1} RETURNING *',
                *values, id
            )

    async def delete(self, id: Any) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.execute(f'DELETE FROM {self.table_name} WHERE id = $1', id)
            return 'DELETE' in result
