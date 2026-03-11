from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.interfaces import UnitOfWork
from src.core.interfaces.repositories import (
    OrderRepository,
    ProductRepository,
    SurveyRepository,
    UserRepository,
)
from src.infrastructure.database.repositories import (
    SQLAlchemyOrderRepository,
    SQLAlchemyProductRepository,
    SQLAlchemySurveyRepository,
    SQLAlchemyUserRepository,
)


class SQLAlchemyUoW(UnitOfWork):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        self._session_maker = session_maker
        self._session: AsyncSession | None = None
        self._user: SQLAlchemyUserRepository | None = None
        self._product: SQLAlchemyProductRepository | None = None
        self._survey: SQLAlchemySurveyRepository | None = None
        self._order: SQLAlchemyOrderRepository | None = None

    @property
    def _current_session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("UoW is not entered. Use 'async with uow:'")
        return self._session

    async def __aenter__(self) -> "SQLAlchemyUoW":
        self._session = self._session_maker()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._session is not None:
            if exc_type is not None:
                await self._session.rollback()
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        await self._current_session.commit()

    async def rollback(self) -> None:
        await self._current_session.rollback()

    @property
    def user(self) -> UserRepository:
        if self._user is None:
            self._user = SQLAlchemyUserRepository(self._current_session)
        return self._user

    @property
    def product(self) -> ProductRepository:
        if self._product is None:
            self._product = SQLAlchemyProductRepository(self._current_session)
        return self._product

    @property
    def survey(self) -> SurveyRepository:
        if self._survey is None:
            self._survey = SQLAlchemySurveyRepository(self._current_session)
        return self._survey

    @property
    def order(self) -> OrderRepository:
        if self._order is None:
            self._order = SQLAlchemyOrderRepository(self._current_session)
        return self._order
