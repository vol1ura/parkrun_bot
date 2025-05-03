from typing import Optional, Dict, Any

from repositories.athlete_repository import AthleteRepository


class AthleteService:
    def __init__(self, athlete_repository: AthleteRepository):
        self.athlete_repository = athlete_repository

    async def find_athlete_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Find an athlete by user ID"""
        return await self.athlete_repository.find_by_user_id(user_id)

    async def find_athlete_by_id(self, athlete_id: int) -> Optional[Dict[str, Any]]:
        """Find an athlete by ID"""
        return await self.athlete_repository.find_by_id(athlete_id)

    async def find_athlete_by_code(self, code_type: str, code_value: Any) -> Optional[Dict[str, Any]]:
        """Find an athlete by a specific code type"""
        return await self.athlete_repository.find_by_code(code_type, code_value)

    async def find_athlete_with_club(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Find an athlete with club information by Telegram ID"""
        return await self.athlete_repository.find_with_club(telegram_id)

    async def find_athlete_with_home_event(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Find an athlete with home event information by Telegram ID"""
        return await self.athlete_repository.find_with_home_event(telegram_id)

    def get_athlete_code(self, athlete: Dict[str, Any]) -> int:
        """Get the athlete code based on available codes"""
        return self.athlete_repository.get_athlete_code(athlete)

    async def create_athlete(self, athlete_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new athlete"""
        return await self.athlete_repository.create(athlete_data)

    async def update_athlete(self, athlete_id: int, athlete_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing athlete"""
        return await self.athlete_repository.update(athlete_id, athlete_data)
