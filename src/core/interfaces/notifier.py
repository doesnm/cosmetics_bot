from abc import ABC, abstractmethod

from src.core.models import Order, RecommendationResult, SurveyAnswer, User


class ManagerNotifier(ABC):
    @abstractmethod
    async def notify_contact_request(
        self,
        user: User,
        survey: SurveyAnswer | None = None,
        recommendation: RecommendationResult | None = None,
    ) -> None: ...

    @abstractmethod
    async def notify_ai_failure(
        self, user: User, survey: SurveyAnswer, error: str
    ) -> None: ...

    @abstractmethod
    async def notify_order(self, user: User, order: Order): ...
