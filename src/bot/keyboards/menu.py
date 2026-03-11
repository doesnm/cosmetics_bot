from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fluentogram import TranslatorRunner

from src.core.enums import Category

_CATEGORY_LABEL_KEYS: dict[Category, str] = {
    Category.SKINCARE: "category-skincare",
}


def main_menu_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("menu-select-cosmetics"),
                    callback_data="start_survey",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("menu-contact-manager"),
                    callback_data="contact_manager",
                ),
            ],
        ],
    )


def category_keyboard(
    categories: list[Category],
    i18n: TranslatorRunner,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=i18n.get(
                    _CATEGORY_LABEL_KEYS.get(cat, cat.value),
                ),
                callback_data=f"category:{cat.value}",
            )
        ]
        for cat in categories
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
