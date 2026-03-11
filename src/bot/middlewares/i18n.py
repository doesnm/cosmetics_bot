from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from fluentogram import TranslatorHub

from src.bot.i18n import resolve_locale


class I18nMiddleware(BaseMiddleware):
    def __init__(self, hub: TranslatorHub) -> None:
        super().__init__()
        self._hub = hub

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        locale = resolve_locale(user.language_code if user else None)

        data["i18n"] = self._hub.get_translator_by_locale(locale)
        data["locale"] = locale
        return await handler(event, data)
