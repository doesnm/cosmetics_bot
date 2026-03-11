from abc import ABC, abstractmethod

from src.core.interfaces.repositories import (
    OrderRepository,
    ProductRepository,
    SurveyRepository,
    UserRepository,
)


class UnitOfWork(ABC):
    @property
    @abstractmethod
    def user(self) -> UserRepository: ...

    @property
    @abstractmethod
    def product(self) -> ProductRepository: ...

    @property
    @abstractmethod
    def survey(self) -> SurveyRepository: ...

    @property
    @abstractmethod
    def order(self) -> OrderRepository: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork": ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...

