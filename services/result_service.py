from typing import Optional, Dict, Any, List
import pandas as pd

from repositories.result_repository import ResultRepository


class ResultService:
    def __init__(self, result_repository: ResultRepository):
        self.result_repository = result_repository

    async def find_result_by_id(self, result_id: int) -> Optional[Dict[str, Any]]:
        """Find a result by ID"""
        return await self.result_repository.find_by_id(result_id)

    async def find_results_by_activity_id(self, activity_id: int) -> List[Dict[str, Any]]:
        """Find results by activity ID"""
        return await self.result_repository.find_by_activity_id(activity_id)

    async def get_user_results(self, telegram_id: int) -> pd.DataFrame:
        """Get all results for a user by Telegram ID"""
        return await self.result_repository.get_user_results(telegram_id)

    async def create_result(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new result"""
        return await self.result_repository.create(result_data)

    async def update_result(self, result_id: int, result_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing result"""
        return await self.result_repository.update(result_id, result_data)
