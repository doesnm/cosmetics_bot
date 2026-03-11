from dataclasses import dataclass, field

import structlog

from src.core.interfaces.repositories.product import ProductFilters
from src.core.interfaces.uow import UnitOfWork
from src.core.models.product import Product
from src.core.models.survey import SurveyAnswer

logger = structlog.get_logger()

_DEFAULT_RELAXATION_ORDER = [
    "preferred_brands",
    "budget",
    "min_rating",
    "attributes",
]


@dataclass
class ProductSearchResult:
    products: list[Product]
    relaxed_filters: list[str] = field(default_factory=list)


class ProductService:
    def __init__(
        self,
        uow: UnitOfWork,
        relaxation_order: list[str] | None = None,
        min_results: int = 1,
    ) -> None:
        self._uow = uow
        self._relaxation_order = relaxation_order or _DEFAULT_RELAXATION_ORDER
        self._min_results = min_results

    async def search_for_survey(
        self,
        survey: SurveyAnswer,
    ) -> ProductSearchResult:
        filters = self._survey_to_filters(survey)

        async with self._uow:
            products = await self._uow.product.search(filters)

            if len(products) >= self._min_results:
                return ProductSearchResult(products=products)

            return await self._search_with_relaxation(filters)

    async def _search_with_relaxation(
        self,
        original_filters: ProductFilters,
    ) -> ProductSearchResult:
        relaxed: list[str] = []
        current = original_filters

        for filter_name in self._relaxation_order:
            current = self._relax_filter(current, filter_name)
            relaxed.append(filter_name)

            products = await self._uow.product.search(current)
            logger.info(
                "Search with relaxation",
                relaxed=relaxed,
                found=len(products),
            )

            if len(products) >= self._min_results:
                return ProductSearchResult(
                    products=products,
                    relaxed_filters=relaxed,
                )

        # fully relaxed — return whatever we have
        products = await self._uow.product.search(current)
        return ProductSearchResult(
            products=products,
            relaxed_filters=relaxed,
        )

    @staticmethod
    def _survey_to_filters(survey: SurveyAnswer) -> ProductFilters:
        return ProductFilters(
            category=survey.category,
            gender=survey.gender,
            budget=survey.budget,
            min_rating=survey.min_rating,
            preferred_brands=survey.preferred_brands,
            attributes=survey.category_answers,
            excluded_ingredients=survey.excluded_ingredients,
        )

    @staticmethod
    def _relax_filter(
        filters: ProductFilters,
        filter_name: str,
    ) -> ProductFilters:
        overrides: dict = {
            "preferred_brands": {"preferred_brands": []},
            "budget": {"budget": None},
            "min_rating": {"min_rating": None},
            "attributes": {"attributes": {}},
        }
        changes = overrides.get(filter_name, {})

        data = {
            "category": filters.category,
            "gender": filters.gender,
            "budget": filters.budget,
            "min_rating": filters.min_rating,
            "preferred_brands": list(filters.preferred_brands),
            "attributes": dict(filters.attributes),
            "excluded_ingredients": list(filters.excluded_ingredients),
            "limit": filters.limit,
        }
        data.update(changes)
        return ProductFilters(**data)

