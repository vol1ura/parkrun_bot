import pandas as pd
from contextlib import asynccontextmanager

from repositories.user_repository import UserRepository
from repositories.result_repository import ResultRepository
from s95.personal import PersonalResults


class StatisticsService:
    def __init__(self, user_repository: UserRepository, result_repository: ResultRepository):
        self.user_repository = user_repository
        self.result_repository = result_repository

    async def get_user_results(self, telegram_id: int) -> pd.DataFrame:
        """Get all results for a user by Telegram ID"""
        return await self.result_repository.get_user_results(telegram_id)

    @asynccontextmanager
    async def get_history_chart(self, telegram_id: int):
        """Generate a history chart for a user"""
        personal_results = PersonalResults(telegram_id)
        async with personal_results.history() as chart:
            yield chart

    @asynccontextmanager
    async def get_personal_bests_chart(self, telegram_id: int):
        """Generate a personal bests chart for a user"""
        personal_results = PersonalResults(telegram_id)
        async with personal_results.personal_bests() as chart:
            yield chart

    @asynccontextmanager
    async def get_tourism_chart(self, telegram_id: int):
        """Generate a tourism chart for a user"""
        personal_results = PersonalResults(telegram_id)
        async with personal_results.tourism() as chart:
            yield chart

    @asynccontextmanager
    async def get_last_runs_chart(self, telegram_id: int):
        """Generate a last runs chart for a user"""
        personal_results = PersonalResults(telegram_id)
        async with personal_results.last_runs() as chart:
            yield chart
