from typing import Optional, Dict, Any, List
import asyncpg

from repositories.postgres_repository import PostgresRepository


class EventRepository(PostgresRepository):
    def __init__(self, pool: asyncpg.Pool):
        super().__init__(pool, 'events')
        self.FRIENDS_EVENT_IDS = [4, 31]  # ID of the 'S95 & friends' event on production

    async def find_all_except_friends(self) -> List[Dict[str, Any]]:
        """Find all events except the 'friends' event"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                'SELECT * FROM events WHERE id != ALL($1) ORDER BY id',
                self.FRIENDS_EVENT_IDS
            )

    async def find_by_id_except_friends(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Find an event by ID, excluding the 'friends' event"""
        if event_id in self.FRIENDS_EVENT_IDS:
            return None
        return await self.find_by_id(event_id)

    async def find_telegram_channel(self, event_id: int) -> Optional[str]:
        """Find the Telegram channel link for an event"""
        async with self.pool.acquire() as conn:
            link = await conn.fetchrow(
                'SELECT link FROM contacts WHERE event_id = $1 AND contact_type = 3',
                event_id
            )
            return link and link['link']
