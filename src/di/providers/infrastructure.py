from aiogram import Bot
from dishka import Provider, Scope, provide

from src.bot.i18n import create_translator_hub
from src.config import Settings
from src.core.interfaces.notifier import ManagerNotifier
from src.infrastructure.notifications.telegram_notifier import (
    TelegramManagerNotifier,
)
from src.infrastructure.survey_config.registry import SurveyFlowRegistry
from src.services.prompt_builder import PromptBuilder


class InfrastructureProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_bot(self, settings: Settings) -> Bot:
        return Bot(token=settings.bot_token)

    @provide(scope=Scope.APP)
    def provide_survey_registry(self) -> SurveyFlowRegistry:
        return SurveyFlowRegistry()

    @provide(scope=Scope.APP)
    def provide_prompt_builder(self) -> PromptBuilder:
        return PromptBuilder()

    @provide(scope=Scope.APP)
    def provide_notifier(
        self,
        bot: Bot,
        settings: Settings,
    ) -> ManagerNotifier:
        hub = create_translator_hub()
        manager_i18n = hub.get_translator_by_locale(
            settings.manager_locale,
        )
        return TelegramManagerNotifier(
            bot=bot,
            manager_chat_id=settings.manager_chat_id,
            i18n=manager_i18n,
        )
