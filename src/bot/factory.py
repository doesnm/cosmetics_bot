from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.handlers import create_root_router
from src.bot.i18n import create_translator_hub
from src.bot.middlewares import (
    ErrorHandlerMiddleware,
    I18nMiddleware,
    UserRegisterMiddleware,
)


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())

    hub = create_translator_hub()

    dp.update.middleware(ErrorHandlerMiddleware())
    dp.update.middleware(I18nMiddleware(hub))
    dp.update.middleware(UserRegisterMiddleware())

    root_router = create_root_router()
    dp.include_router(root_router)

    return dp
