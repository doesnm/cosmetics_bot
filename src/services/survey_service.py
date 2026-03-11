import structlog

from src.core.enums import AgeRange, BudgetRange, Category, Gender
from src.core.interfaces.uow import UnitOfWork
from src.core.models.survey import SurveyAnswer
from src.infrastructure.survey_config.registry import SurveyFlowRegistry
from src.infrastructure.survey_config.steps import SurveyStep

logger = structlog.get_logger()

_DIRECT_FIELDS = {
    "gender",
    "age_range",
    "category",
    "budget",
    "min_rating",
}

_LIST_FIELDS = {
    "preferred_brands",
    "allergens",
    "excluded_ingredients",
}


class SurveyService:
    def __init__(
        self,
        uow: UnitOfWork,
        flow_registry: SurveyFlowRegistry,
    ) -> None:
        self._uow = uow
        self._registry = flow_registry

    def get_steps(self, category: Category) -> list[SurveyStep]:
        flow = self._registry.get_flow(category)
        return flow.get_steps()

    def available_categories(self) -> list[Category]:
        return self._registry.available_categories()

    async def complete_survey(
        self,
        telegram_id: int,
        category: Category,
        answers: dict[str, list[str]],
    ) -> SurveyAnswer:
        """
        Build SurveyAnswer from raw answers dict and save to DB.

        Args:
            telegram_id: user id
            category: selected category
            answers: {step_key: [selected_values]}
                     e.g. {"gender": ["female"], "skin_type": ["oily"],
                           "skin_concerns": ["acne", "pores"]}
        """
        survey = self._build_survey_answer(telegram_id, category, answers)

        async with self._uow:
            saved = await self._uow.survey.save(survey)
            await self._uow.commit()

        logger.info(
            "Survey completed",
            telegram_id=telegram_id,
            category=category.value,
        )
        return saved

    async def get_latest_survey(self, telegram_id: int) -> SurveyAnswer | None:
        async with self._uow:
            return await self._uow.survey.get_latest_by_user(telegram_id)

    @staticmethod
    def _build_survey_answer(
        telegram_id: int,
        category: Category,
        answers: dict[str, list[str]],
    ) -> SurveyAnswer:
        survey = SurveyAnswer(
            user_telegram_id=telegram_id,
            category=category,
        )

        for key, values in answers.items():
            if not values:
                continue

            if key in _DIRECT_FIELDS:
                value = values[0]  # direct fields are single-select
                match key:
                    case "gender":
                        survey.gender = Gender(value)
                    case "age_range":
                        survey.age_range = AgeRange(value)
                    case "budget":
                        survey.budget = BudgetRange(value)
                    case "min_rating":
                        survey.min_rating = float(value)

            elif key in _LIST_FIELDS:
                match key:
                    case "preferred_brands":
                        survey.preferred_brands = values
                    case "allergens":
                        survey.allergens = values
                    case "excluded_ingredients":
                        survey.excluded_ingredients = values

            else:
                # category-specific → goes into category_answers
                survey.category_answers[key] = values

        return survey

    @staticmethod
    def parse_text_input(text: str) -> list[str]:
        return [item.strip() for item in text.split(",") if item.strip()]
