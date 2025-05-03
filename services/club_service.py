from typing import Optional, Dict, Any, List

from repositories.club_repository import ClubRepository


class ClubService:
    def __init__(self, club_repository: ClubRepository):
        self.club_repository = club_repository

    async def find_club_by_id(self, club_id: int) -> Optional[Dict[str, Any]]:
        """Find a club by ID"""
        return await self.club_repository.find_by_id(club_id)

    async def find_club_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find a club by name (case insensitive, partial match)"""
        return await self.club_repository.find_by_name(name)

    async def find_all_clubs(self) -> List[Dict[str, Any]]:
        """Find all clubs"""
        return await self.club_repository.find_all()

    async def create_club(self, club_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new club"""
        return await self.club_repository.create(club_data)

    async def update_club(self, club_id: int, club_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing club"""
        return await self.club_repository.update(club_id, club_data)
