from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from src.infrastructure.database.base import Base, TimestampMixin


class UserORM(TimestampMixin, Base):
    __tablename__ = "users"
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False
    )
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    username: Mapped[str] = mapped_column(String(32), nullable=True)
    language_code: Mapped[str] = mapped_column(String(10), nullable=True)
