from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    async def find_by_id(self, id: Any) -> Optional[T]:
        """Find an entity by its ID"""
        pass

    @abstractmethod
    async def find_by(self, field: str, value: Any) -> Optional[T]:
        """Find an entity by a specific field"""
        pass

    @abstractmethod
    async def find_all(self) -> List[T]:
        """Find all entities"""
        pass

    @abstractmethod
    async def create(self, entity: Dict[str, Any]) -> T:
        """Create a new entity"""
        pass

    @abstractmethod
    async def update(self, id: Any, entity: Dict[str, Any]) -> Optional[T]:
        """Update an existing entity"""
        pass

    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Delete an entity by its ID"""
        pass
