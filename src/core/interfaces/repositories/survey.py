from abc import ABC, abstractmethod

from src.core.models.survey import SurveyAnswer


class SurveyRepository(ABC):
    @abstractmethod
    async def save(self, survey: SurveyAnswer) -> SurveyAnswer: ...

    @abstractmethod
    async def get_latest_by_user(
        self,
        telegram_id: int,
    ) -> SurveyAnswer | None: ...
