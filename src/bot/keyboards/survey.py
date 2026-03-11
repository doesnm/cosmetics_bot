from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fluentogram import TranslatorRunner

from src.bot.keyboards.common import back_button, done_button, skip_button
from src.infrastructure.survey_config.steps import SurveyStep

_TWO_COLUMNS_THRESHOLD = 6


def step_keyboard(
    step: SurveyStep,
    i18n: TranslatorRunner,
    selected: list[str] | None = None,
    show_back: bool = False,
) -> InlineKeyboardMarkup:
    selected = selected or []
    buttons: list[InlineKeyboardButton] = []

    for option in step.options:
        label = i18n.get(option.label_key)

        if step.is_multi_select:
            prefix = "✅ " if option.value in selected else ""
            callback = f"survey_toggle:{step.key}:{option.value}"
        else:
            prefix = ""
            callback = f"survey_answer:{step.key}:{option.value}"

        buttons.append(
            InlineKeyboardButton(
                text=f"{prefix}{label}",
                callback_data=callback,
            ),
        )

    # arrange in rows
    if len(buttons) >= _TWO_COLUMNS_THRESHOLD:
        rows = _to_two_columns(buttons)
    else:
        rows = [[b] for b in buttons]

    # bottom controls
    bottom: list[InlineKeyboardButton] = []
    if show_back:
        bottom.append(back_button(i18n))
    if step.is_multi_select and selected:
        bottom.append(done_button(i18n))
    if step.is_skippable:
        bottom.append(skip_button(i18n))
    if bottom:
        rows.append(bottom)

    return InlineKeyboardMarkup(inline_keyboard=rows)


def text_input_keyboard(
    i18n: TranslatorRunner,
    show_back: bool = False,
) -> InlineKeyboardMarkup:
    buttons: list[InlineKeyboardButton] = []
    if show_back:
        buttons.append(back_button(i18n))
    buttons.append(skip_button(i18n))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def _to_two_columns(
    buttons: list[InlineKeyboardButton],
) -> list[list[InlineKeyboardButton]]:
    rows: list[list[InlineKeyboardButton]] = []
    for i in range(0, len(buttons), 2):
        row = buttons[i : i + 2]
        rows.append(row)
    return rows

