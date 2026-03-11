from dishka import Provider, Scope, provide

from src.config import Settings


class ConfigProvider(Provider):
    scope = Scope.APP

    @provide
    def provide_settings(self) -> Settings:
        return Settings()
