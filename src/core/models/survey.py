from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.core.enums import AgeRange, BudgetRange, Category, Gender


@dataclass
class SurveyAnswer:
    user_telegram_id: int

    gender: Gender | None = None
    age_range: AgeRange | None = None
    category: Category | None = None
    budget: BudgetRange | None = None
    min_rating: float | None = None

    category_answers: dict[str, list[str]] = field(default_factory=dict)

    allergens: list[str] = field(default_factory=list)
    excluded_ingredients: list[str] = field(default_factory=list)
    preferred_brands: list[str] = field(default_factory=list)

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
