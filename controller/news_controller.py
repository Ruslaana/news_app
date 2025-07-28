from aiogram import Dispatcher, types
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)
from service.news_service import first_lunch_handler, translate_to_ukrainian

LATEST_NEWS = {}


async def start_command(message: types.Message):
    latest_new = first_lunch_handler()
    if not latest_new:
        await message.answer("Error fetching the latest news.")
        return

    user_id = message.from_user.id
    LATEST_NEWS[user_id] = latest_new

    title_uk = translate_to_ukrainian(latest_new.title)
    content_uk = translate_to_ukrainian(latest_new.content)

    short_text = (
        f"<b>{title_uk}</b>\n"
        f"<i>{latest_new.publication_time} | {latest_new.author}</i>\n\n"
        f"{content_uk[:300]}..."
    )

    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("📖 Прочитати новину",
                             callback_data="show_full_news")
    )

    if latest_new.image_url:
        await message.answer_photo(
            photo=latest_new.image_url,
            caption=short_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        await message.answer(
            short_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )


async def show_full_news(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    news = LATEST_NEWS.get(user_id)
    content_uk = translate_to_ukrainian(news.content)

    if not news:
        await callback_query.message.answer("Error fetching the latest news.")
        await callback_query.answer()
        return

    chunks = [content_uk[i:i+4000] for i in range(0, len(content_uk), 4000)]
    for chunk in chunks:
        await callback_query.message.answer(
            chunk,
            disable_web_page_preview=True
        )

    await callback_query.answer()


async def echo_message(message: types.Message):
    await message.answer(f"Ви написали: {message.text}")


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_callback_query_handler(
        show_full_news, lambda c: c.data == "show_full_news")
    dp.register_message_handler(echo_message)
