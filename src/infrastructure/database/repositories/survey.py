from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import AgeRange, BudgetRange, Category, Gender
from src.core.interfaces.repositories.survey import SurveyRepository
from src.core.models.survey import SurveyAnswer
from src.infrastructure.database.models.survey import SurveyORM


class SQLAlchemySurveyRepository(SurveyRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, survey: SurveyAnswer) -> SurveyAnswer:
        orm = self._to_orm(survey)
        self._session.add(orm)
        await self._session.flush()
        return self._to_domain(orm)

    async def get_latest_by_user(
        self,
        telegram_id: int,
    ) -> SurveyAnswer | None:
        stmt = (
            select(SurveyORM)
            .where(SurveyORM.user_telegram_id == telegram_id)
            .order_by(SurveyORM.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm is None:
            return None
        return self._to_domain(orm)

    @staticmethod
    def _to_orm(survey: SurveyAnswer) -> SurveyORM:
        return SurveyORM(
            user_telegram_id=survey.user_telegram_id,
            gender=survey.gender.value if survey.gender else None,
            age_range=survey.age_range.value if survey.age_range else None,
            category=survey.category.value if survey.category else None,
            budget=survey.budget.value if survey.budget else None,
            min_rating=survey.min_rating,
            preferred_brands=survey.preferred_brands,
            allergens=survey.allergens,
            excluded_ingredients=survey.excluded_ingredients,
            category_answers=survey.category_answers,
        )

    @staticmethod
    def _to_domain(orm: SurveyORM) -> SurveyAnswer:
        return SurveyAnswer(
            user_telegram_id=orm.user_telegram_id,
            gender=Gender(orm.gender) if orm.gender else None,
            age_range=AgeRange(orm.age_range) if orm.age_range else None,
            category=Category(orm.category) if orm.category else None,
            budget=BudgetRange(orm.budget) if orm.budget else None,
            min_rating=float(orm.min_rating) if orm.min_rating else None,
            preferred_brands=orm.preferred_brands or [],
            allergens=orm.allergens or [],
            excluded_ingredients=orm.excluded_ingredients or [],
            category_answers=orm.category_answers or {},
            created_at=orm.created_at,
        )
