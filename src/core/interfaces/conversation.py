from abc import ABC, abstractmethod

from src.core.interfaces.ai_provider import ChatMessage


class ConversationRepository(ABC):
    @abstractmethod
    async def get_history(
        self,
        user_id: int,
        session_id: str,
    ) -> list[ChatMessage]: ...

    @abstractmethod
    async def append_message(
        self,
        user_id: int,
        session_id: str,
        message: ChatMessage,
    ) -> None: ...

    @abstractmethod
    async def append_messages(
        self,
        user_id: int,
        session_id: str,
        messages: list[ChatMessage],
    ) -> None: ...

    @abstractmethod
    async def clear(
        self,
        user_id: int,
        session_id: str,
    ) -> None: ...
