from decimal import Decimal

from sqlalchemy import orm, select, update, not_
from sqlalchemy.engine import result
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import BudgetRange, Category, Gender
from src.core.interfaces.repositories.product import (
    ProductFilters,
    ProductRepository,
)
from src.core.models import Product
from src.infrastructure.database.models import ProductORM

_BUDGET_RANGES: dict[BudgetRange, tuple[int, int | None]] = {
    BudgetRange.LOW: (0, 15),
    BudgetRange.MEDIUM: (15, 40),
    BudgetRange.HIGH: (40, 80),
    BudgetRange.PREMIUM: (80, None),
}


class SQLAlchemyProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def search(self, filters: ProductFilters) -> list[Product]:
        stmt = select(ProductORM)
        condition = self._build_conditions(filters)

        if condition:
            stmt = stmt.where(*condition)

        stmt = stmt.order_by(ProductORM.rating.desc()).limit(filters.limit)

        result = await self._session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def get_by_id(self, product_id: int) -> Product | None:
        stmt = select(ProductORM).where(ProductORM.id == product_id)

        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()

        if orm is None:
            return None
        return self._to_domain(orm)

    async def get_by_ids(self, product_ids: list[int]) -> list[Product]:
        if not product_ids:
            return []

        stmt = select(ProductORM).where(ProductORM.id.in_(product_ids))
        result = await self._session.execute(stmt)

        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def update_tg_file_id(
        self,
        product_id: int,
        file_id: str,
    ) -> None:
        stmt = (
            update(ProductORM)
            .where(ProductORM.id == product_id)
            .values(tg_file_id=file_id)
        )
        await self._session.execute(stmt)

    @staticmethod
    def _build_conditions(filters: ProductFilters) -> list:
        conditions: list = []

        if filters.category is not None:
            conditions.append(ProductORM.category == filters.category.value)

        if filters.gender is not None:
            conditions.append(
                ProductORM.gender.in_([filters.gender.value, Gender.UNISEX.value])
            )

        if filters.budget is not None:
            price_range = _BUDGET_RANGES.get(filters.budget)
            if price_range:
                low, high = price_range
                conditions.append(ProductORM.price >= low)
                if high is not None:
                    conditions.append(ProductORM.price < high)

        if filters.min_rating is not None:
            conditions.append(ProductORM.rating >= filters.min_rating)

        if filters.preferred_brands:
            conditions.append(ProductORM.brand.in_(filters.preferred_brands))

        # JSONB attributes: {"skin_type": ["oily"]} → product must contain these
        for key, values in filters.attributes.items():
            if values:
                conditions.append(ProductORM.attributes.contains({key: values}))

        if filters.excluded_ingredients:
            for ingredient in filters.excluded_ingredients:
                conditions.append(
                    not_(ProductORM.attributes["ingredients"].contains([ingredient]))
                )

        return conditions

    @staticmethod
    def _to_domain(orm: ProductORM) -> Product:
        return Product(
            id=orm.id,
            name=orm.name,
            brand=orm.brand,
            category=Category(orm.category),
            gender=Gender(orm.gender),
            price=Decimal(str(orm.price)),
            currency=orm.currency,
            rating=float(orm.rating),
            description=orm.description,
            attributes=orm.attributes or {},
            image_url=orm.image_url,
            tg_file_id=orm.tg_file_id,
        )
