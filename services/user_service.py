from typing import Optional, Dict, Any

from repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def find_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Find a user by Telegram ID"""
        return await self.user_repository.find_by_telegram_id(telegram_id)

    async def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find a user by email"""
        return await self.user_repository.find_by_email(email)

    async def find_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Find a user by ID"""
        return await self.user_repository.find_by_id(user_id)

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        return await self.user_repository.create(user_data)

    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing user"""
        return await self.user_repository.update(user_id, user_data)
