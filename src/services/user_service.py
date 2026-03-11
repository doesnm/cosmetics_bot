from src.core.interfaces.uow import UnitOfWork
from src.core.models.user import User


class UserService:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def get_or_create(
        self, telegram_id, first_name, username, language_code
    ) -> User:
        async with self._uow:
            user = User(
                telegram_id=telegram_id,
                first_name=first_name,
                username=username,
                language_code=language_code,
            )
            result = await self._uow.user.upsert(user)
            await self._uow.commit()
            return result

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        async with self._uow:
            return await self._uow.user.get_by_telegram_id(telegram_id)
