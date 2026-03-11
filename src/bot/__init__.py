from aiogram import Router

from src.bot.handlers import order, recommendation, start
from src.bot.handlers.survey import router as survey_router


def create_root_router() -> Router:
    root = Router()
    root.include_router(start.router)
    root.include_router(survey_router.router)
    root.include_router(recommendation.router)
    root.include_router(order.router)
    return root
