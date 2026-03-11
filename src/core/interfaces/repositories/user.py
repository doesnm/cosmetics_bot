from abc import ABC, abstractmethod

from src.core.models import User


class UserRepository(ABC):
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> User | None: ...

    @abstractmethod
    async def upsert(self, user: User) -> User: ...
