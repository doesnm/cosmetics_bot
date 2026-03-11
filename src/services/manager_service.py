import structlog

from src.core.interfaces.notifier import ManagerNotifier
from src.core.interfaces.uow import UnitOfWork
from src.core.models.recommendation import RecommendationResult
from src.core.models.survey import SurveyAnswer
from src.core.models.user import User

logger = structlog.get_logger()


class ManagerService:
    def __init__(self, uow: UnitOfWork, notifier: ManagerNotifier):
        self._uow = uow
        self._notifier = notifier

    async def handle_contact_request(
        self,
        telegram_id: int,
        recommendation: RecommendationResult | None = None,
    ) -> None:
        async with self._uow:
            user = await self._uow.user.get_by_telegram_id(telegram_id)
            if user is None:
                logger.warning(
                    "Contact request from unknown user",
                    telegram_id=telegram_id,
                )
                user = User(
                    telegram_id=telegram_id,
                    first_name="Unknown",
                )

            survey = await self._uow.survey.get_latest_by_user(telegram_id)

        await self._notifier.notify_contact_request(
            user=user,
            survey=survey,
            recommendation=recommendation,
        )

        logger.info(
            "Manager notified: contact request",
            telegram_id=telegram_id,
            has_survey=survey is not None,
            has_recommendation=recommendation is not None,
        )

    async def handle_ai_failure(
        self,
        telegram_id: int,
        survey: SurveyAnswer,
        error: str,
    ) -> None:
        async with self._uow:
            user = await self._uow.user.get_by_telegram_id(telegram_id)
            if user is None:
                user = User(
                    telegram_id=telegram_id,
                    first_name="Unknown",
                )

        await self._notifier.notify_ai_failure(
            user=user,
            survey=survey,
            error=error,
        )

        logger.info(
            "Manager notified: AI failure",
            telegram_id=telegram_id,
            error=error,
        )

    async def handle_new_order(
        self,
        telegram_id: int,
        order_id: int,
    ) -> None:
        async with self._uow:
            user = await self._uow.user.get_by_telegram_id(telegram_id)
            if user is None:
                user = User(
                    telegram_id=telegram_id,
                    first_name="Unknown",
                )
            order = await self._uow.order.get_by_id(order_id)

        if order is None:
            logger.error("Order not found for notification", order_id=order_id)
            return

        await self._notifier.notify_order(user=user, order=order)

        logger.info(
            "Manager notified: new order",
            telegram_id=telegram_id,
            order_id=order_id,
        )

