from decimal import Decimal

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

from src.bot.keyboards.menu import main_menu_keyboard
from src.bot.states.survey import OrderStates
from src.core.enums import Category, Gender
from src.core.models.product import Product
from src.services.manager_service import ManagerService
from src.services.order_service import OrderService

router = Router()


def order_confirm_keyboard(
    i18n: TranslatorRunner,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("order-confirm"),
                    callback_data="order_confirm",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-cancel"),
                    callback_data="order_cancel",
                ),
            ],
        ],
    )


@router.callback_query(F.data == "order_recommended")
@inject
async def order_recommended(
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

    if not rec_data:
        await message.edit_text(
            i18n.get("error-no-products"),
            reply_markup=main_menu_keyboard(i18n),
        )
        await callback.answer()
        return

    # show order summary
    text_parts = [i18n.get("order-summary-title"), ""]

    total = Decimal("0")
    for r in rec_data:
        price = Decimal(r["price"])
        total += price
        text_parts.append(
            f"• {r['brand']} — {r['name']}\n  💰 ${price}\n",
        )

    text_parts.append(f"\n<b>{i18n.get('order-total', total=str(total))}</b>")

    await state.set_state(OrderStates.confirming)
    await message.edit_text(
        "\n".join(text_parts),
        reply_markup=order_confirm_keyboard(i18n),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(
    OrderStates.confirming,
    F.data == "order_confirm",
)
@inject
async def order_confirm(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: TranslatorRunner,
    order_service: FromDishka[OrderService],
    manager_service: FromDishka[ManagerService],
) -> None:
    message = callback.message
    if not isinstance(message, Message):
        await callback.answer()
        return

    data = await state.get_data()
    rec_data = data.get("recommendations", [])
    category_value = data.get("category", Category.SKINCARE.value)

    products = [
        Product(
            id=r["product_id"],
            name=r["name"],
            brand=r["brand"],
            price=Decimal(r["price"]),
            category=Category(category_value),
            gender=Gender.UNISEX,
        )
        for r in rec_data
    ]

    order = await order_service.create_from_recommendations(
        user_telegram_id=callback.from_user.id,
        products=products,
    )

    if order.id is not None:
        await manager_service.handle_new_order(
            telegram_id=callback.from_user.id,
            order_id=order.id,
        )

    await state.clear()

    await message.edit_text(
        i18n.get(
            "order-created",
            id=str(order.id or 0),
            total=str(order.total),
        ),
        reply_markup=main_menu_keyboard(i18n),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(
    OrderStates.confirming,
    F.data == "order_cancel",
)
async def order_cancel(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: TranslatorRunner,
) -> None:
    message = callback.message
    if not isinstance(message, Message):
        await callback.answer()
        return

    await state.set_state(None)
    await message.edit_text(
        i18n.get("order-cancelled"),
        reply_markup=main_menu_keyboard(i18n),
    )
    await callback.answer()
