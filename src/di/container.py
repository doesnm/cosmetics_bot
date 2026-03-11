from dishka import AsyncContainer, make_async_container

from src.di.providers.ai import AIProviderDI
from src.di.providers.config import ConfigProvider
from src.di.providers.database import DatabaseProvider
from src.di.providers.infrastructure import InfrastructureProvider
from src.di.providers.services import ServiceProvider


def create_container() -> AsyncContainer:
    return make_async_container(
        ConfigProvider(),
        DatabaseProvider(),
        AIProviderDI(),
        InfrastructureProvider(),
        ServiceProvider(),
    )
