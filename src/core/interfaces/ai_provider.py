from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


class AIProvider(ABC):
    @abstractmethod
    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
    ) -> str: ...

    @abstractmethod
    async def complete_json(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
    ) -> str: ...
