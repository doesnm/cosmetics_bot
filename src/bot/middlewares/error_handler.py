from collections.abc import Awaitable, Callable
from typing import Any

import structlog
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from fluentogram import TranslatorRunner

logger = structlog.get_logger()


class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logger.exception(
                "Unhandled error in handler",
                error=str(e),
                event_type=type(event).__name__,
            )

            i18n: TranslatorRunner | None = data.get("i18n")
            error_text = i18n.get("error-generic") if i18n else "An error occurred."

            try:
                if isinstance(event, CallbackQuery) and event.message:
                    await event.message.answer(error_text)
                    await event.answer()
                elif isinstance(event, Message):
                    await event.answer(error_text)
            except Exception:
                pass

            return None
