import asyncio

import structlog

from src.core.exceptions import (
    AIFatalError,
    AIRetryableError,
    AIRetryExhaustedError,
)
from src.core.interfaces.ai_provider import AIProvider, ChatMessage

logger = structlog.get_logger()


class RetryableAIProvider(AIProvider):
    def __init__(
        self,
        provider: AIProvider,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
    ):
        self._provider = provider
        self._max_retries = max_retries
        self._base_delay = base_delay
        self._max_delay = max_delay

    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
    ) -> str:
        return await self._with_retry(
            self._provider.complete,
            messages,
            max_tokens=max_tokens,
        )

    async def complete_json(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
    ) -> str:
        return await self._with_retry(
            self._provider.complete_json,
            messages,
            max_tokens=max_tokens,
        )

    async def _with_retry(self, method, *args, **kwargs) -> str:
        last_error: Exception | None = None

        for attempt in range(1, self._max_retries + 1):
            try:
                return await method(*args, **kwargs)

            except AIFatalError:
                raise

            except AIRetryableError as e:
                last_error = e
                delay = min(
                    self._base_delay * (2 ** (attempt - 1)),
                    self._max_delay,
                )
                logger.warning(
                    "AI retryable error, retrying",
                    attempt=attempt,
                    max_retries=self._max_retries,
                    delay=delay,
                    status_code=e.status_code,
                    error=str(e),
                )
                if attempt < self._max_retries:
                    await asyncio.sleep(delay)

        raise AIRetryExhaustedError(
            message=f"All {self._max_retries} attempts failed",
            attempts=self._max_retries,
            last_error=last_error,  # type: ignore[arg-type]
        )
