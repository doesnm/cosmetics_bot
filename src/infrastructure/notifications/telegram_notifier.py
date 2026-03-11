import structlog
from aiogram import Bot
from fluentogram import TranslatorRunner

from src.core.interfaces.notifier import ManagerNotifier
from src.core.models.order import Order
from src.core.models.recommendation import RecommendationResult
from src.core.models.survey import SurveyAnswer
from src.core.models.user import User

logger = structlog.get_logger()


class TelegramManagerNotifier(ManagerNotifier):
    def __init__(
        self,
        bot: Bot,
        manager_chat_id: int,
        i18n: TranslatorRunner,
    ) -> None:
        self._bot = bot
        self._chat_id = manager_chat_id
        self._i18n = i18n

    async def notify_contact_request(
        self,
        user: User,
        survey: SurveyAnswer | None = None,
        recommendation: RecommendationResult | None = None,
    ) -> None:
        parts = [
            self._i18n.get("manager-contact-request-title"),
            "",
            self._format_user(user),
        ]

        if survey:
            parts.append("")
            parts.append(self._format_survey(survey))

        if recommendation and recommendation.recommendations:
            parts.append("")
            parts.append(self._format_recommendations(recommendation))

        await self._send("\n".join(parts))

    async def notify_ai_failure(
        self,
        user: User,
        survey: SurveyAnswer,
        error: str,
    ) -> None:
        parts = [
            self._i18n.get("manager-ai-failure-title"),
            "",
            self._format_user(user),
            "",
            self._format_survey(survey),
            "",
            self._i18n.get("manager-ai-failure-error", error=error[:500]),
        ]
        await self._send("\n".join(parts))

    async def notify_order(
        self,
        user: User,
        order: Order,
    ) -> None:
        items_text = "\n".join(
            f"  • {item.product_name} — ${item.price} × {item.quantity}"
            for item in order.items
        )

        parts = [
            self._i18n.get("manager-new-order-title"),
            "",
            self._format_user(user),
            "",
            self._i18n.get("manager-order-id", id=str(order.id)),
            self._i18n.get(
                "manager-order-status",
                status=order.status.value,
            ),
            self._i18n.get("manager-order-items-label"),
            items_text,
            self._i18n.get("manager-order-total", total=str(order.total)),
        ]
        await self._send("\n".join(parts))

    async def _send(self, text: str) -> None:
        try:
            await self._bot.send_message(
                chat_id=self._chat_id,
                text=text,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(
                "Failed to notify manager",
                chat_id=self._chat_id,
                error=str(e),
            )

    def _format_user(self, user: User) -> str:
        lines = [
            self._i18n.get("manager-user-label", name=user.first_name),
        ]
        if user.username:
            lines.append(
                self._i18n.get(
                    "manager-user-username",
                    username=user.username,
                ),
            )
        lines.append(
            self._i18n.get("manager-user-id", id=str(user.telegram_id)),
        )
        if user.language_code:
            lines.append(
                self._i18n.get(
                    "manager-user-lang",
                    lang=user.language_code,
                ),
            )
        return "\n".join(lines)

    def _format_survey(self, survey: SurveyAnswer) -> str:
        lines = [self._i18n.get("manager-survey-label")]

        if survey.category:
            lines.append(
                f"  • {self._i18n.get('manager-survey-category', value=survey.category.value)}",
            )
        if survey.gender:
            lines.append(
                f"  • {self._i18n.get('manager-survey-gender', value=survey.gender.value)}",
            )
        if survey.age_range:
            lines.append(
                f"  • {self._i18n.get('manager-survey-age', value=survey.age_range.value)}",
            )
        if survey.budget:
            lines.append(
                f"  • {self._i18n.get('manager-survey-budget', value=survey.budget.value)}",
            )

        for key, values in survey.category_answers.items():
            label = key.replace("_", " ").title()
            lines.append(f"  • {label}: {', '.join(values)}")

        if survey.allergens:
            lines.append(
                f"  • {self._i18n.get('manager-survey-allergens', value=', '.join(survey.allergens))}",
            )
        if survey.preferred_brands:
            lines.append(
                f"  • {self._i18n.get('manager-survey-brands', value=', '.join(survey.preferred_brands))}",
            )

        return "\n".join(lines)

    def _format_recommendations(
        self,
        result: RecommendationResult,
    ) -> str:
        lines = [self._i18n.get("manager-recommendations-label")]

        for rec in result.recommendations:
            lines.append(
                f"  • {rec.product.brand} — {rec.product.name} (${rec.product.price})",
            )

        if result.relaxed_filters:
            lines.append(
                self._i18n.get(
                    "manager-recommendations-relaxed",
                    filters=", ".join(result.relaxed_filters),
                ),
            )

        return "\n".join(lines)
