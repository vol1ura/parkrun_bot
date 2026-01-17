from typing import Dict, Any, List
import asyncpg
import pandas as pd

from repositories.postgres_repository import PostgresRepository


class ResultRepository(PostgresRepository):
    def __init__(self, pool: asyncpg.Pool):
        super().__init__(pool, 'results')

    async def find_by_activity_id(self, activity_id: int) -> List[Dict[str, Any]]:
        """Find results by activity ID"""
        async with self.pool.acquire() as conn:
            query = """SELECT position, total_time, athlete_id, athletes.name, clubs.name FROM results
                LEFT OUTER JOIN athletes ON athletes.id = results.athlete_id
                LEFT OUTER JOIN clubs ON clubs.id = athletes.club_id
                WHERE results.activity_id = $1
                ORDER BY results.position ASC
            """
            return await conn.fetch(query, activity_id)

    async def get_user_results(self, telegram_id: int) -> pd.DataFrame:
        """Get all results for a user by Telegram ID"""
        async with self.pool.acquire() as conn:
            query = """SELECT results.position, results.total_time, activities.date, events.name FROM results
                INNER JOIN activities ON activities.id = results.activity_id
                INNER JOIN events ON events.id = activities.event_id
                INNER JOIN athletes ON athletes.id = results.athlete_id
                INNER JOIN users ON users.id = athletes.user_id
                WHERE users.telegram_id = $1 AND activities.published = TRUE
                ORDER BY activities.date DESC
            """
            data = await conn.fetch(query, telegram_id)

            df = pd.DataFrame(data, columns=pd.Index(['Pos', 'Time', 'Run Date', 'Event']))
            df['m'] = df['Time'] / 60
            return df
