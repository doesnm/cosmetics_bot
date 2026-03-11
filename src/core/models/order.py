from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import StrEnum


class OrderStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    CANCELLED = "cancelled"


@dataclass
class OrderItem:
    product_id: int
    product_name: str
    price: Decimal
    quantity: int = 1


@dataclass
class Order:
    id: int | None = None
    user_telegram_id: int = 0
    items: list[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def total(self) -> Decimal:
        return sum((item.price * item.quantity for item in self.items), Decimal(0))
