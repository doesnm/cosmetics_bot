from typing import Literal, Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    bot_token: str
    log_level: str = "INFO"

    manager_chat_id: int
    manager_username: str = ""
    manager_locale: str = "ru"

    ai_provider: Literal["gemini", "grok"]
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.1-flash-preview"
    grok_api_key: str | None = None
    grok_model: str = "grok-4-fast-non-reasoning"

    ai_max_retries: int = 3
    ai_retry_base_delay: float = 1.0
    ai_retry_max_delay: float = 30.0

    database_url: str

    @model_validator(mode="after")
    def validate_ai_provider_has_key(self) -> Self:
        key_map = {
            "gemini": self.gemini_api_key,
            "grok": self.grok_api_key,
        }
        if not key_map.get(self.ai_provider):
            raise ValueError(
                f"AI provider '{self.ai_provider}' selected "
                f"but '{self.ai_provider}_api_key' is not set"
            )
        return self
