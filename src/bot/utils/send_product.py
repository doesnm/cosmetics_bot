from aiogram import Bot
from aiogram.types import URLInputFile

from src.core.interfaces.uow import UnitOfWork
from src.core.models.product import Product


async def send_product_photo(
    bot: Bot,
    chat_id: int,
    product: Product,
    caption: str,
    uow: UnitOfWork,
    **kwargs,
) -> None:
    """Send product photo. Cache file_id after first upload."""

    if not product.image_url and not product.tg_file_id:
        # no photo — send text only
        await bot.send_message(chat_id, caption, **kwargs)
        return

    if product.tg_file_id:
        # fast path — already uploaded to Telegram
        msg = await bot.send_photo(
            chat_id,
            photo=product.tg_file_id,
            caption=caption,
            **kwargs,
        )
        return

    # first time — upload from URL
    photo = URLInputFile(str(product.image_url))

    msg = await bot.send_photo(
        chat_id,
        photo=photo,
        caption=caption,
        **kwargs,
    )

    # save file_id for future use
    if msg.photo:
        file_id = msg.photo[-1].file_id  # largest size
        async with uow:
            await uow.product.update_tg_file_id(product.id, file_id)
            await uow.commit()
