from dataclasses import dataclass, field

from src.core.models.product import Product
from src.core.models.survey import SurveyAnswer


@dataclass
class Recommendation:
    product: Product
    reasoning: str
    match_score: float | None = None


@dataclass
class RecommendationResult:
    recommendations: list[Recommendation]
    survey: SurveyAnswer
    relaxed_filters: list[str] = field(default_factory=list)
    ai_succeeded: bool = True
    warning_message: str | None = None
