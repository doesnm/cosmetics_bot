from abc import ABC, abstractmethod

from src.core.enums import AgeRange, BudgetRange, Gender
from src.infrastructure.survey_config.steps import StepOption, SurveyStep


GENDER_STEP = SurveyStep(
    key="gender",
    question_key="step-gender-question",
    options=[
        StepOption(value=Gender.FEMALE, label_key="step-gender-female"),
        StepOption(value=Gender.MALE, label_key="step-gender-male"),
        StepOption(value=Gender.UNISEX, label_key="step-gender-unisex"),
    ],
)

AGE_STEP = SurveyStep(
    key="age_range",
    question_key="step-age-question",
    options=[
        StepOption(value=AgeRange.UNDER_18, label_key="step-age-under-18"),
        StepOption(value=AgeRange.AGE_18_24, label_key="step-age-18-24"),
        StepOption(value=AgeRange.AGE_25_34, label_key="step-age-25-34"),
        StepOption(value=AgeRange.AGE_35_44, label_key="step-age-35-44"),
        StepOption(value=AgeRange.AGE_45_PLUS, label_key="step-age-45-plus"),
    ],
)

BUDGET_STEP = SurveyStep(
    key="budget",
    question_key="step-budget-question",
    options=[
        StepOption(value=BudgetRange.LOW, label_key="step-budget-low"),
        StepOption(value=BudgetRange.MEDIUM, label_key="step-budget-medium"),
        StepOption(value=BudgetRange.HIGH, label_key="step-budget-high"),
        StepOption(value=BudgetRange.PREMIUM, label_key="step-budget-premium"),
    ],
    is_skippable=True,
)

ALLERGENS_STEP = SurveyStep(
    key="allergens",
    question_key="step-allergens-question",
    options=[
        StepOption(value="fragrance", label_key="step-allergen-fragrance"),
        StepOption(value="alcohol", label_key="step-allergen-alcohol"),
        StepOption(value="parabens", label_key="step-allergen-parabens"),
        StepOption(value="essential_oils", label_key="step-allergen-essential-oils"),
        StepOption(value="retinol", label_key="step-allergen-retinol"),
        StepOption(value="acids", label_key="step-allergen-acids"),
        StepOption(value="niacinamide", label_key="step-allergen-niacinamide"),
    ],
    is_multi_select=True,
    is_skippable=True,
)

BRANDS_STEP = SurveyStep(
    key="preferred_brands",
    question_key="step-brands-question",
    is_text_input=True,
    is_skippable=True,
)

RATING_STEP = SurveyStep(
    key="min_rating",
    question_key="step-rating-question",
    options=[
        StepOption(value="3.0", label_key="step-rating-3"),
        StepOption(value="3.5", label_key="step-rating-3-5"),
        StepOption(value="4.0", label_key="step-rating-4"),
        StepOption(value="4.5", label_key="step-rating-4-5"),
    ],
    is_skippable=True,
)


class BaseSurveyFlow(ABC):
    def get_steps(self) -> list[SurveyStep]:
        return [
            *self._common_start_steps(),
            *self._category_steps(),
            *self._common_end_steps(),
        ]

    def _common_start_steps(self) -> list[SurveyStep]:
        return [GENDER_STEP, AGE_STEP]

    @abstractmethod
    def _category_steps(self) -> list[SurveyStep]: ...

    def _common_end_steps(self) -> list[SurveyStep]:
        return [BUDGET_STEP, ALLERGENS_STEP, BRANDS_STEP, RATING_STEP]

