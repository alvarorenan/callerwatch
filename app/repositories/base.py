from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')


class BaseRepository(Generic[T], ABC):
    """Base repository following Repository pattern"""

    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def create(self, obj: T) -> T:
        """Create a new entity"""
        pass

    @abstractmethod
    async def get_by_id(self, id: Any) -> Optional[T]:
        """Get entity by ID"""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination"""
        pass

    @abstractmethod
    async def update(self, id: Any, obj: T) -> Optional[T]:
        """Update entity"""
        pass

    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Delete entity"""
        pass
