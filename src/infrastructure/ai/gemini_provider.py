import structlog
from google import genai
from google.genai import types as genai_types
from google.genai.errors import ServerError, ClientError, APIError

from src.core.exceptions import AIFatalError, AIRetryableError
from src.core.interfaces.ai_provider import AIProvider, ChatMessage

logger = structlog.get_logger()


_ROLE_MAP = {
    "user": "user",
    "assistant": "model",
}

_RETRYABLE_CODES = {429, 500, 502, 503, 504}


class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, model: str):
        self._client = genai.Client(api_key=api_key)
        self._model = model

    async def complete(
        self, messages: list[ChatMessage], *, max_tokens: int | None = None
    ) -> str:
        return await self._call(
            messages=messages,
            max_tokens=max_tokens,
        )

    async def complete_json(
        self, messages: list[ChatMessage], *, max_tokens: int | None = None
    ) -> str:
        return await self._call(
            messages=messages,
            max_tokens=max_tokens,
            response_mime_type="application/json",
        )

    async def _call(
        self,
        messages: list[ChatMessage],
        max_tokens: int | None = None,
        response_mime_type: str | None = None,
    ) -> str:
        system_instruction, contents = self._split_messages(messages)

        config = genai_types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            system_instruction=system_instruction,
            response_mime_type=response_mime_type,
        )

        try:
            response = await self._client.aio.models.generate_content(
                model=self._model, contents=contents, config=config
            )
            text = response.text or ""
            logger.debug(
                "AI response received",
                provider="gemini",
                model=self._model,
            )
            return text
        except ClientError as e:
            if e.code in _RETRYABLE_CODES:
                raise AIRetryableError(
                    f"GenAI Error: {e}",
                    status_code=e.code,
                ) from e
            raise AIFatalError(
                f"Gen AI Client Error: {e.message}\nDetails: {e.details}",
                status_code=e.code,
            ) from e
        except ServerError as e:
            raise AIRetryableError(
                f"GenAI Server error: {e.message}",
                status_code=e.code,
            ) from e
        except APIError as e:
            raise AIFatalError(
                f"GenAI API Error {e.message}", status_code=e.code
            ) from e

    @staticmethod
    def _split_messages(
        messages: list[ChatMessage],
    ) -> tuple[str | None, list[genai_types.Content]]:
        system_parts: list[str] = []
        contents: list[genai_types.Content] = []

        for msg in messages:
            if msg.role == "system":
                system_parts.append(msg.content)
                continue

            gemini_role = _ROLE_MAP.get(msg.role, msg.role)
            contents.append(
                genai_types.Content(
                    role=gemini_role,
                    parts=[genai_types.Part(text=msg.content)],
                ),
            )

        system_instruction = "\n\n".join(system_parts) if system_parts else None
        return system_instruction, contents
