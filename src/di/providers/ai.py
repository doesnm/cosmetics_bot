from dishka import Provider, Scope, provide

from src.config import Settings
from src.core.interfaces.ai_provider import AIProvider
from src.infrastructure.ai import GeminiProvider, OpenAIProvider, RetryableAIProvider


class AIProviderDI(Provider):
    @provide(scope=Scope.APP)
    def provide_ai_provider(self, settings: Settings) -> AIProvider:
        base_provider = self._create_base_provider(settings)
        return RetryableAIProvider(
            provider=base_provider,
            max_retries=settings.ai_max_retries,
            base_delay=settings.ai_retry_base_delay,
            max_delay=settings.ai_retry_max_delay,
        )

    @staticmethod
    def _create_base_provider(settings: Settings) -> AIProvider:
        match settings.ai_provider:
            case "gemini":
                return GeminiProvider(
                    api_key=str(settings.gemini_api_key),
                    model=settings.gemini_model,
                )
            case "grok":
                return OpenAIProvider(
                    api_key=str(settings.grok_api_key),
                    model=settings.grok_model,
                    base_url="https://api.x.ai/v1",
                )
            case _:
                raise ValueError(f"Unknown AI provider: {settings.ai_provider}")
