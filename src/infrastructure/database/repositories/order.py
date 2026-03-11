from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.interfaces.repositories.order import OrderRepository
from src.core.models.order import Order, OrderItem, OrderStatus
from src.infrastructure.database.models.order import OrderItemORM, OrderORM


class SQLAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, order: Order) -> Order:
        orm = OrderORM(
            user_telegram_id=order.user_telegram_id,
            status=order.status.value,
            items=[
                OrderItemORM(
                    product_id=item.product_id,
                    product_name=item.product_name,
                    price=item.price,
                    quantity=item.quantity,
                )
                for item in order.items
            ],
        )

        self._session.add(orm)
        await self._session.flush()
        return self._to_domain(orm)

    async def get_by_id(self, order_id: int) -> Order | None:
        stmt = (
            select(OrderORM)
            .where(OrderORM.id == order_id)
            .options(selectinload(OrderORM.items))
        )

        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()

        if orm is None:
            return None
        return self._to_domain(orm)

    async def update_status(self, order_id: int, status: str) -> None:
        stmt = update(OrderORM).where(OrderORM.id == order_id).values(status=status)
        await self._session.execute(stmt)

    @staticmethod
    def _to_domain(orm: OrderORM) -> Order:
        return Order(
            id=orm.id,
            user_telegram_id=orm.user_telegram_id,
            status=OrderStatus(orm.status),
            created_at=orm.created_at,
            items=[
                OrderItem(
                    product_id=item.product_id,
                    product_name=item.product_name,
                    price=Decimal(str(item.price)),
                    quantity=item.quantity,
                )
                for item in orm.items
            ],
        )
