from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.interfaces.repositories.user import UserRepository
from src.core.models.user import User
from src.infrastructure.database.models.user import UserORM


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(UserORM).where(UserORM.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm is None:
            return None
        return self._to_domain(orm)

    async def upsert(self, user: User) -> User:
        stmt = insert(UserORM).values(
            telegram_id=user.telegram_id,
            first_name=user.first_name,
            username=user.username,
            language_code=user.language_code,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["telegram_id"],
            set_={
                "first_name": stmt.excluded.first_name,
                "username": stmt.excluded.username,
                "language_code": stmt.excluded.language_code,
            },
        ).returning(UserORM)

        result = await self._session.execute(stmt)
        orm = result.scalar_one()
        return self._to_domain(orm)

    @staticmethod
    def _to_domain(orm: UserORM) -> User:
        return User(
            telegram_id=orm.telegram_id,
            first_name=orm.first_name,
            username=orm.username,
            language_code=orm.language_code,
            created_at=orm.created_at,
        )

