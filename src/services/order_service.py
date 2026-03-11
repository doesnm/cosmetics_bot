import structlog

from src.core.interfaces.uow import UnitOfWork
from src.core.models.order import Order, OrderItem, OrderStatus
from src.core.models.product import Product

logger = structlog.get_logger()


class OrderService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def create_from_recommendations(
        self,
        user_telegram_id: int,
        products: list[Product],
    ) -> Order:
        items = [
            OrderItem(
                product_id=product.id,
                product_name=f"{product.brand} — {product.name}",
                price=product.price,
                quantity=1,
            )
            for product in products
        ]

        order = Order(
            user_telegram_id=user_telegram_id,
            items=items,
            status=OrderStatus.PENDING,
        )

        async with self._uow:
            created = await self._uow.order.create(order)
            await self._uow.commit()

            logger.info(
                "Order created",
                order_id=created.id,
                user_id=user_telegram_id,
                total=str(created.total),
                items_count=len(items),
            )
            return created

    async def get_order(self, order_id: int) -> Order | None:
        async with self._uow:
            return await self._uow.order.get_by_id(order_id)

    async def update_status(
        self,
        order_id: int,
        status: OrderStatus,
    ) -> None:
        async with self._uow:
            await self._uow.order.update_status(order_id, status.value)
            await self._uow.commit()

            logger.info(
                "Order status updated",
                order_id=order_id,
                new_status=status.value,
            )
