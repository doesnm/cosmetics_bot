from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_engine(database_url: str):
    return create_async_engine(
        database_url,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )


def create_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
