import asyncio

import structlog
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from dishka.integrations.aiogram import setup_dishka

from src.bot.factory import create_dispatcher
from src.config import Settings
from src.di import create_container

logger = structlog.get_logger()


async def main() -> None:
    settings = Settings()

    container = create_container()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = create_dispatcher()
    setup_dishka(container=container, router=dp)

    logger.info("Bot starting...")

    try:
        await dp.start_polling(bot)
    finally:
        await container.close()
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
