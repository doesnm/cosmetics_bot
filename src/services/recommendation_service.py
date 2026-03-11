import json

import structlog

from src.core.exceptions import AIProviderError, AIRetryExhaustedError
from src.core.interfaces.ai_provider import AIProvider
from src.core.interfaces.uow import UnitOfWork
from src.core.models.recommendation import (
    Recommendation,
    RecommendationResult,
)
from src.core.models.survey import SurveyAnswer
from src.services.product_service import ProductService
from src.services.prompt_builder import PromptBuilder

logger = structlog.get_logger()


class RecommendationService:
    def __init__(
        self,
        ai_provider: AIProvider,
        product_service: ProductService,
        prompt_builder: PromptBuilder,
        uow: UnitOfWork,
    ):
        self._ai = ai_provider
        self._product_service = product_service
        self._prompt_builder = prompt_builder
        self._uow = uow

    async def get_recommendations(self, survey: SurveyAnswer) -> RecommendationResult:
        # 1. Search products with relaxation
        search_result = await self._product_service.search_for_survey(survey)

        if not search_result.products:
            logger.warning("No products found even after relaxation")
            return RecommendationResult(
                recommendations=[],
                survey=survey,
                relaxed_filters=search_result.relaxed_filters,
                ai_succeeded=False,
                warning_message="К сожалению, подходящих товаров не найдено.",
            )

        # 2. Build prompt
        messages = self._prompt_builder.build_recommendation_messages(
            survey=survey,
            products=search_result.products,
            relaxed_filters=search_result.relaxed_filters,
        )

        # 3. Call AI
        try:
            raw_json = await self._ai.complete_json(messages)
            parsed = self._parse_ai_response(raw_json)
        except AIRetryExhaustedError as e:
            logger.error("AI retry exhausted", error=str(e))
            return RecommendationResult(
                recommendations=[],
                survey=survey,
                relaxed_filters=search_result.relaxed_filters,
                ai_succeeded=False,
                warning_message="Сервис подбора временно недоступен.",
            )
        except AIProviderError as e:
            logger.error("AI fatal error", error=str(e))
            return RecommendationResult(
                recommendations=[],
                survey=survey,
                relaxed_filters=search_result.relaxed_filters,
                ai_succeeded=False,
                warning_message="Ошибка сервиса подбора.",
            )

        # 4. Map product_ids to actual products
        product_map = {p.id: p for p in search_result.products}
        recommendations: list[Recommendation] = []

        for item in parsed["recommendations"]:
            product_id = item["product_id"]
            product = product_map.get(product_id)
            if product is None:
                logger.warning("AI returned unknown product_id", product_id=product_id)
                continue
            recommendations.append(
                Recommendation(
                    product=product,
                    reasoning=item.get("reasoning", ""),
                ),
            )

        warning = None
        if search_result.relaxed_filters:
            relaxed_str = ", ".join(search_result.relaxed_filters)
            warning = f"Точных совпадений не найдено. Ослаблены фильтры: {relaxed_str}."

        return RecommendationResult(
            recommendations=recommendations,
            survey=survey,
            relaxed_filters=search_result.relaxed_filters,
            ai_succeeded=True,
            warning_message=warning,
        )

    @staticmethod
    def _parse_ai_response(raw_json: str) -> dict:
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError as e:
            logger.error("AI returned invalid JSON", raw=raw_json[:500])
            raise AIProviderError(f"Invalid JSON from AI: {e}") from e

        if "recommendations" not in data:
            logger.error("AI response missing 'recommendations'", data=data)
            raise AIProviderError("AI response missing 'recommendations' key")

        return data
