from src.core.interfaces.ai_provider import ChatMessage
from src.core.models.product import Product
from src.core.models.survey import SurveyAnswer

_RECOMMENDATION_SYSTEM_PROMPT = """\
You are an expert cosmetics consultant.

You will receive:
1. A customer profile (survey answers)
2. A list of available products

Your task:
- Select exactly 3 best matching products
- Explain why each product suits this customer
- If filters were relaxed, warn the customer about limited matches

Respond ONLY with valid JSON:
{
  "recommendations": [
    {
      "product_id": <int>,
      "reasoning": "<why this product fits, 2-3 sentences>"
    }
  ]
}
"""

_CHAT_SYSTEM_PROMPT_TEMPLATE = """\
You are a friendly cosmetics consultant chatbot.
You help customers choose beauty products.

{context_block}

Guidelines:
- Be helpful, concise, and professional
- If the customer asks about products you recommended, refer to them
- If you don't know something, say so honestly
- You can suggest adjusting the search criteria if needed
- Respond in the same language the customer writes in
"""

_CONTEXT_SURVEY_BLOCK = """\
Customer profile:
{survey_text}
"""

_CONTEXT_PRODUCTS_BLOCK = """\
Previously recommended products:
{products_text}
"""


class PromptBuilder:
    def build_recommendation_messages(
        self,
        survey: SurveyAnswer,
        products: list[Product],
        relaxed_filters: list[str],
    ) -> list[ChatMessage]:
        system = ChatMessage(role="system", content=_RECOMMENDATION_SYSTEM_PROMPT)

        user_parts = [
            f"Customer profile:\n{self._format_survey(survey)}",
        ]
        if relaxed_filters:
            user_parts.append(
                f"\n⚠️ Note: exact matches were not found. "
                f"The following filters were relaxed: {', '.join(relaxed_filters)}. "
                f"Please mention this to the customer in your reasoning.",
            )
        user_parts.append(
            f"\nAvailable products ({len(products)}):\n"
            f"{self._format_products(products)}",
        )

        user = ChatMessage(role="user", content="\n".join(user_parts))
        return [system, user]

    def build_chat_system_message(
        self,
        survey: SurveyAnswer | None = None,
        recommended_products: list[Product] | None = None,
    ) -> ChatMessage:
        context_parts: list[str] = []

        if survey:
            context_parts.append(
                _CONTEXT_SURVEY_BLOCK.format(
                    survey_text=self._format_survey(survey),
                ),
            )
        if recommended_products:
            context_parts.append(
                _CONTEXT_PRODUCTS_BLOCK.format(
                    products_text=self._format_products_short(
                        recommended_products,
                    ),
                ),
            )

        context_block = "\n".join(context_parts) if context_parts else ""
        content = _CHAT_SYSTEM_PROMPT_TEMPLATE.format(
            context_block=context_block,
        )
        return ChatMessage(role="system", content=content)

    def _format_survey(self, survey: SurveyAnswer) -> str:
        lines: list[str] = []
        if survey.gender:
            lines.append(f"- Gender: {survey.gender.value}")
        if survey.age_range:
            lines.append(f"- Age range: {survey.age_range.value}")
        if survey.category:
            lines.append(f"- Category: {survey.category.value}")
        if survey.budget:
            lines.append(f"- Budget: {survey.budget.value}")
        if survey.min_rating:
            lines.append(f"- Minimum rating: {survey.min_rating}")
        if survey.preferred_brands:
            lines.append(f"- Preferred brands: {', '.join(survey.preferred_brands)}")
        if survey.allergens:
            lines.append(f"- Allergens to avoid: {', '.join(survey.allergens)}")
        if survey.excluded_ingredients:
            lines.append(
                f"- Excluded ingredients: {', '.join(survey.excluded_ingredients)}",
            )

        for key, values in survey.category_answers.items():
            label = key.replace("_", " ").title()
            lines.append(f"- {label}: {', '.join(values)}")

        return "\n".join(lines) if lines else "No specific preferences"

    def _format_products(self, products: list[Product]) -> str:
        parts: list[str] = []
        for p in products:
            attrs = ""
            if p.attributes:
                attrs_items = [f"{k}: {', '.join(v)}" for k, v in p.attributes.items()]
                attrs = f" | {' | '.join(attrs_items)}"

            parts.append(
                f"[ID:{p.id}] {p.brand} - {p.name} | "
                f"${p.price} | Rating: {p.rating}{attrs}",
            )
        return "\n".join(parts)

    def _format_products_short(self, products: list[Product]) -> str:
        return "\n".join(f"- {p.brand} {p.name} (${p.price})" for p in products)
