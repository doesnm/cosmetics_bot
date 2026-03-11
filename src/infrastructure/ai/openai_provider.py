import structlog

from openai import APIConnectionError, APIStatusError, AsyncOpenAI, RateLimitError

from src.core.exceptions import AIFatalError, AIRetryableError
from src.core.interfaces.ai_provider import AIProvider, ChatMessage

logger = structlog.get_logger()

_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class OpenAIProvider(AIProvider):
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str | None = None,
    ):
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self._provider_name = "openai" if base_url is None else base_url

    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
    ) -> str:
        return await self._call(
            messages=messages,
            max_tokens=max_tokens,
        )

    async def complete_json(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
    ) -> str:
        return await self._call(
            messages=messages,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

    async def _call(
        self,
        messages: list[ChatMessage],
        max_tokens: int | None,
        response_format: dict | None = None,
    ) -> str:
        kwargs: dict = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }

        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        if response_format is not None:
            kwargs["response_format"] = response_format

        try:
            response = await self._client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or ""

            logger.debug(
                "AI response received",
                provider=self._provider_name,
                model=self._model,
                tokens=response.usage.total_tokens if response.usage else None,
            )
            return content
        except RateLimitError as e:
            raise AIRetryableError(
                f"Rate limit: {e}",
                status_code=429,
            ) from e
        except APIStatusError as e:
            if e.status_code in _RETRYABLE_STATUS_CODES:
                raise AIRetryableError(
                    f"Server error: {e}",
                    status_code=e.status_code,
                ) from e
            raise AIFatalError(
                f"API error: {e}",
                status_code=e.status_code,
            ) from e
        except APIConnectionError as e:
            raise AIRetryableError(
                f"Connection error: {e}",
            ) from e
