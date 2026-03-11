import structlog

from src.core.exceptions import AIProviderError
from src.core.interfaces.ai_provider import AIProvider, ChatMessage
from src.core.interfaces.conversation import ConversationRepository
from src.core.models.product import Product
from src.core.models.survey import SurveyAnswer
from src.services.prompt_builder import PromptBuilder

logger = structlog.get_logger()


class ChatService:
    def __init__(
        self,
        ai_provider: AIProvider,
        conversation_repo: ConversationRepository,
        prompt_builder: PromptBuilder,
    ) -> None:
        self._ai = ai_provider
        self._conversations = conversation_repo
        self._prompt_builder = prompt_builder

    async def start_session(
        self,
        user_id: int,
        session_id: str,
        survey: SurveyAnswer | None = None,
        recommended_products: list[Product] | None = None,
    ) -> None:
        await self._conversations.clear(user_id, session_id)
        system_msg = self._prompt_builder.build_chat_system_message(
            survey=survey,
            recommended_products=recommended_products,
        )
        await self._conversations.append_message(
            user_id,
            session_id,
            system_msg,
        )

    async def send_message(
        self,
        user_id: int,
        session_id: str,
        user_text: str,
    ) -> str:
        user_msg = ChatMessage(role="user", content=user_text)
        await self._conversations.append_message(
            user_id,
            session_id,
            user_msg,
        )

        history = await self._conversations.get_history(user_id, session_id)

        try:
            response_text = await self._ai.complete(history)
        except AIProviderError:
            logger.error("AI failed during chat", user_id=user_id)
            raise

        assistant_msg = ChatMessage(role="assistant", content=response_text)
        await self._conversations.append_message(
            user_id,
            session_id,
            assistant_msg,
        )

        return response_text
