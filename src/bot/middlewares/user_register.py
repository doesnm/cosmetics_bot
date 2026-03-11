from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from dishka import AsyncContainer

from src.services.user_service import UserService


class UserRegisterMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")

        if user is not None:
            container: AsyncContainer = data["dishka_container"]
            user_service = await container.get(UserService)
            await user_service.get_or_create(
                telegram_id=user.id,
                first_name=user.first_name,
                username=user.username,
                language_code=user.language_code,
            )

        return await handler(event, data)
