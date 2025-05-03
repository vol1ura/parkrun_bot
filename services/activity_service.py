from typing import Optional, Dict, Any, Tuple
import pandas as pd

from repositories.activity_repository import ActivityRepository
from repositories.result_repository import ResultRepository
from s95.helpers import time_conv


class ActivityService:
    def __init__(self, activity_repository: ActivityRepository, result_repository: ResultRepository):
        self.activity_repository = activity_repository
        self.result_repository = result_repository

    async def find_activity_by_id(self, activity_id: int) -> Optional[Dict[str, Any]]:
        """Find an activity by ID"""
        return await self.activity_repository.find_by_id(activity_id)

    async def find_latest_activity(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Find the latest activity for a user by Telegram ID"""
        return await self.activity_repository.find_latest_by_telegram_id(telegram_id)

    async def get_latest_results(self, telegram_id: int) -> Optional[Tuple[pd.DataFrame, Any, str, int]]:
        """Get the latest results for a user by Telegram ID"""
        last_activity = await self.activity_repository.find_latest_by_telegram_id(telegram_id)
        if last_activity is None:
            return None

        data = await self.result_repository.find_by_activity_id(last_activity['id'])

        df = pd.DataFrame(data, columns=['Pos', 'Время', 'athlete_id', 'Участник', 'Клуб'])
        df['Время'] = df['Время'].apply(lambda t: time_conv(t))

        return df, last_activity['date'], last_activity['name'], last_activity['athlete_id']

    async def create_activity(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new activity"""
        return await self.activity_repository.create(activity_data)

    async def update_activity(self, activity_id: int, activity_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing activity"""
        return await self.activity_repository.update(activity_id, activity_data)
