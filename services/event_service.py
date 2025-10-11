from typing import Optional, Dict, Any, List

from repositories.event_repository import EventRepository


class EventService:
    def __init__(self, event_repository: EventRepository):
        self.event_repository = event_repository

    async def find_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Find an event by ID"""
        return await self.event_repository.find_by_id_except_friends(event_id)

    async def find_all_events(self) -> List[Dict[str, Any]]:
        """Find all events except the 'friends' event"""
        return await self.event_repository.find_all_except_friends()

    async def find_telegram_channel(self, event_id: int) -> Optional[str]:
        """Find the Telegram channel link for an event"""
        return await self.event_repository.find_telegram_channel(event_id)

    async def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new event"""
        return await self.event_repository.create(event_data)

    async def update_event(self, event_id: int, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing event"""
        return await self.event_repository.update(event_id, event_data)

    async def find_events_by_country(self, country_id: int) -> List[Dict[str, Any]]:
        """Find all events in a specific country"""
        return await self.event_repository.find_by_country(country_id)
