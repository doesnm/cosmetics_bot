from decimal import Decimal
from sqlalchemy import BigInteger, Numeric, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from src.infrastructure.database.base import Base, TimestampMixin


class SurveyORM(TimestampMixin, Base):
    __tablename__ = "surveys"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_telegram_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id")
    )
    gender: Mapped[str] = mapped_column(String(20), nullable=True)
    age_range: Mapped[str] = mapped_column(String, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=True)
    budget: Mapped[str] = mapped_column(String, nullable=True)
    min_rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=0)
    preferred_brands: Mapped[list] = mapped_column(JSONB, server_default="[]")
    allergens: Mapped[list] = mapped_column(JSONB, server_default="[]")
    excluded_ingredients: Mapped[list] = mapped_column(JSONB, server_default="[]")
    category_answers: Mapped[dict] = mapped_column(JSONB, server_default="{}")
