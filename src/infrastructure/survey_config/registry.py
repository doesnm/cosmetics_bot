from src.core.enums import Category
from src.core.exceptions import SurveyFlowNotFoundError
from src.infrastructure.survey_config.base_flow import BaseSurveyFlow
from src.infrastructure.survey_config.flows.skincare import SkincareSurveyFlow


class SurveyFlowRegistry:
    def __init__(self) -> None:
        self._flows: dict[Category, BaseSurveyFlow] = {
            Category.SKINCARE: SkincareSurveyFlow(),
        }

    def get_flow(self, category: Category) -> BaseSurveyFlow:
        flow = self._flows.get(category)
        if flow is None:
            raise SurveyFlowNotFoundError(f"No survey flow for category: {category}")
        return flow

    def available_categories(self) -> list[Category]:
        return list(self._flows.keys())
