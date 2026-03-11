from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from src.config import Settings
from src.core.interfaces.uow import UnitOfWork
from src.infrastructure.database.session import (
    create_engine,
    create_session_maker,
)
from src.infrastructure.database.uow import SQLAlchemyUoW


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_engine(
        self,
        settings: Settings,
    ) -> AsyncIterable[AsyncEngine]:
        engine = create_engine(settings.database_url)
        yield engine
        await engine.dispose()

    @provide(scope=Scope.APP)
    def provide_session_maker(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return create_session_maker(engine)

    @provide(scope=Scope.REQUEST)
    def provide_uow(
        self,
        session_maker: async_sessionmaker[AsyncSession],
    ) -> UnitOfWork:
        return SQLAlchemyUoW(session_maker)
