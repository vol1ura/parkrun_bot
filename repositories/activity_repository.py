from typing import Optional, Dict, Any
import asyncpg

from repositories.postgres_repository import PostgresRepository


class ActivityRepository(PostgresRepository):
    def __init__(self, pool: asyncpg.Pool):
        super().__init__(pool, 'activities')

    async def find_latest_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Find the latest activity for a user by Telegram ID"""
        async with self.pool.acquire() as conn:
            query = """SELECT activities.id, activities.date, events.name, athletes.id AS athlete_id
                FROM results
                INNER JOIN activities ON activities.id = results.activity_id
                INNER JOIN events ON events.id = activities.event_id
                INNER JOIN athletes ON athletes.id = results.athlete_id
                INNER JOIN users ON users.id = athletes.user_id
                WHERE users.telegram_id = $1 AND activities.published = TRUE
                ORDER BY activities.date DESC
                LIMIT 1
            """
            return await conn.fetchrow(query, telegram_id)
