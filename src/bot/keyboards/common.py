from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fluentogram import TranslatorRunner


def back_button(i18n: TranslatorRunner) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=i18n.get("btn-back"),
        callback_data="back",
    )


def cancel_button(i18n: TranslatorRunner) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=i18n.get("btn-cancel"),
        callback_data="cancel",
    )


def skip_button(i18n: TranslatorRunner) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=i18n.get("btn-skip"),
        callback_data="skip",
    )


def done_button(i18n: TranslatorRunner) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=i18n.get("btn-done"),
        callback_data="done",
    )


def cancel_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[cancel_button(i18n)]],
    )
