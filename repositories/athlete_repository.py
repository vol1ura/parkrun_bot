from typing import Optional, Dict, Any
import asyncpg

from repositories.postgres_repository import PostgresRepository
from s95.athlete_code import AthleteCode


class AthleteRepository(PostgresRepository):
    def __init__(self, pool: asyncpg.Pool):
        super().__init__(pool, 'athletes')

    async def find_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Find an athlete by user ID"""
        return await self.find_by('user_id', user_id)

    async def find_by_code(self, code_type: str, code_value: Any) -> Optional[Dict[str, Any]]:
        """Find an athlete by a specific code type (parkrun_code, fiveverst_code, etc.)"""
        return await self.find_by(code_type, code_value)

    async def find_with_club(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Find an athlete with club information by Telegram ID"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                """SELECT athletes.*, clubs.name as club_name
                FROM athletes
                LEFT JOIN clubs ON athletes.club_id = clubs.id
                INNER JOIN users ON users.id = athletes.user_id
                WHERE users.telegram_id = $1""",
                telegram_id
            )

    async def find_with_home_event(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Find an athlete with home event information by Telegram ID"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                """SELECT athletes.*, events.name as event_name
                FROM athletes
                INNER JOIN users ON users.id = athletes.user_id
                LEFT JOIN events ON athletes.event_id = events.id
                WHERE users.telegram_id = $1""",
                telegram_id
            )

    def get_athlete_code(self, athlete: Dict[str, Any]) -> int:
        """Get the athlete code based on available codes"""
        return athlete["parkrun_code"] or athlete["fiveverst_code"] or athlete["runpark_code"] \
            or athlete["parkzhrun_code"] or athlete["id"] + AthleteCode.SAT_5AM_9KM_BORDER
