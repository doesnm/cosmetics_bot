from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorRunner

from src.bot.keyboards.menu import main_menu_keyboard
from src.services.manager_service import ManagerService

router = Router()


@router.message(CommandStart())
@inject
async def cmd_start(
    message: Message,
    state: FSMContext,
    i18n: TranslatorRunner,
) -> None:
    await state.clear()
    name = message.from_user.first_name if message.from_user else ""
    await message.answer(
        i18n.get("start-message", name=name),
        reply_markup=main_menu_keyboard(i18n),
    )


@router.callback_query(lambda c: c.data == "main_menu")
async def back_to_menu(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: TranslatorRunner,
) -> None:
    await state.clear()
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            i18n.get("menu-title"),
            reply_markup=main_menu_keyboard(i18n),
        )

    await callback.answer()


@router.callback_query(lambda c: c.data == "contact_manager")
@inject
async def contact_manager(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
    manager_service: FromDishka[ManagerService],
) -> None:
    await manager_service.handle_contact_request(telegram_id=callback.from_user.id)

    text = i18n.get("manager-request-sent")
    markup = main_menu_keyboard(i18n)

    if isinstance(callback.message, Message):
        await callback.message.edit_text(text, reply_markup=markup)

    await callback.answer()
