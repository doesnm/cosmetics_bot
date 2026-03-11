from sqlalchemy import BigInteger, Integer, Numeric, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database.base import Base, TimestampMixin


class OrderORM(TimestampMixin, Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    user_telegram_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id")
    )
    status: Mapped[str] = mapped_column(String(20), default="pending")

    items: Mapped[list["OrderItemORM"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderItemORM(TimestampMixin, Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.id"),
    )
    product_id: Mapped[int] = mapped_column(Integer)
    product_name: Mapped[str] = mapped_column(String)
    price: Mapped[Numeric] = mapped_column(Numeric(10, 2))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    order: Mapped["OrderORM"] = relationship(back_populates="items")
