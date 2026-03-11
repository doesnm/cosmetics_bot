from abc import ABC, abstractmethod

from src.core.models.order import Order


class OrderRepository(ABC):
    @abstractmethod
    async def create(self, order: Order) -> Order: ...

    @abstractmethod
    async def get_by_id(self, order_id: int) -> Order | None: ...

    @abstractmethod
    async def update_status(
        self,
        order_id: int,
        status: str,
    ) -> None: ...
