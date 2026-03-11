from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorRunner
import structlog

from src.bot.keyboards.menu import main_menu_keyboard
from src.bot.states.survey import ChatStates
from src.core.exceptions import AIProviderError
from src.core.interfaces.ai_provider import AIProvider, ChatMessage
from src.services.manager_service import ManagerService

logger = structlog.get_logger()

router = Router()


def recommendation_keyboard(
    i18n: TranslatorRunner,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("rec-btn-chat"),
                    callback_data="start_chat",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("rec-btn-order"),
                    callback_data="order_recommended",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("rec-btn-contact-manager"),
                    callback_data="contact_manager_with_rec",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("rec-btn-new-survey"),
                    callback_data="start_survey",
                ),
            ],
        ],
    )


def after_chat_keyboard(
    i18n: TranslatorRunner,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("rec-btn-order"),
                    callback_data="order_recommended",
                ),
                InlineKeyboardButton(
                    text=i18n.get("rec-btn-contact-manager"),
                    callback_data="contact_manager_with_rec",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("rec-btn-new-survey"),
                    callback_data="start_survey",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-back"),
                    callback_data="main_menu",
                ),
            ],
        ],
    )


@router.callback_query(F.data == "contact_manager_with_rec")
@inject
async def contact_with_recommendations(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
    manager_service: FromDishka[ManagerService],
) -> None:
    message = callback.message
    if not isinstance(message, Message):
        await callback.answer()
        return

    await manager_service.handle_contact_request(
        telegram_id=callback.from_user.id,
    )
    await message.edit_text(
        i18n.get("rec-manager-got-rec"),
        reply_markup=main_menu_keyboard(i18n),
    )
    await callback.answer()


# --- Chat with AI ---


@router.callback_query(F.data == "start_chat")
async def start_chat(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: TranslatorRunner,
) -> None:
    message = callback.message
    if not isinstance(message, Message):
        await callback.answer()
        return

    data = await state.get_data()
    rec_data = data.get("recommendations", [])

    system_content = (
        "You are a friendly cosmetics consultant. "
        "The customer received these recommendations:\n"
    )
    for r in rec_data:
        system_content += (
            f"- {r['brand']} {r['name']} (${r['price']}): {r['reasoning']}\n"
        )
    system_content += (
        "\nAnswer questions about these products. "
        "Be helpful and concise. "
        "Respond in the same language the customer writes in."
    )

    await state.update_data(
        chat_history=[
            {"role": "system", "content": system_content},
        ],
    )

    await state.set_state(ChatStates.chatting)
    await message.answer(i18n.get("chat-start"))
    await callback.answer()


@router.message(ChatStates.chatting)
@inject
async def handle_chat_message(
    message: Message,
    state: FSMContext,
    i18n: TranslatorRunner,
    ai_provider: FromDishka[AIProvider],
) -> None:
    if not message.text:
        return

    if message.text.startswith("/stop"):
        await state.set_state(None)
        await message.answer(
            i18n.get("chat-stopped"),
            reply_markup=after_chat_keyboard(i18n),
        )
        return

    data = await state.get_data()
    history: list[dict] = data.get("chat_history", [])

    history.append({"role": "user", "content": message.text})

    messages = [ChatMessage(role=m["role"], content=m["content"]) for m in history]

    try:
        response = await ai_provider.complete(messages)
    except AIProviderError as e:
        logger.error(
            "AI chat error",
            user_id=message.from_user.id if message.from_user else None,
            error=str(e),
        )
        await message.answer(i18n.get("chat-ai-error"))
        # remove failed user message from history
        history.pop()
        await state.update_data(chat_history=history)
        return
    except Exception as e:
        logger.exception(
            "Unexpected AI chat error",
            user_id=message.from_user.id if message.from_user else None,
            error=str(e),
        )
        await message.answer(i18n.get("chat-ai-error"))
        history.pop()
        await state.update_data(chat_history=history)
        return

    history.append({"role": "assistant", "content": response})

    # keep last 20 messages + system
    if len(history) > 21:
        history = [history[0]] + history[-20:]

    await state.update_data(chat_history=history)

    # add /stop hint
    stop_hint = f"\n\n<i>{i18n.get('chat-stop-hint')}</i>"
    await message.answer(
        response + stop_hint,
        parse_mode="HTML",
    )
