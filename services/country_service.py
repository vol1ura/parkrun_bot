from typing import Optional, Dict, Any, List

from repositories.country_repository import CountryRepository


class CountryService:
    def __init__(self, country_repository: CountryRepository):
        self.country_repository = country_repository

    async def find_all_countries(self) -> List[Dict[str, Any]]:
        """Find all countries"""
        return await self.country_repository.find_all()

    async def find_country_by_id(self, country_id: int) -> Optional[Dict[str, Any]]:
        """Find a country by ID"""
        return await self.country_repository.find_by_id(country_id)
