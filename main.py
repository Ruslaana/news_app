from aiogram import Bot, Dispatcher
from configs.news_conf import TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from service.news_service import AntiFloodMiddleware, logger
from controller.news_controller import register_handlers

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

dp.middleware.setup(AntiFloodMiddleware())

register_handlers(dp)

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    logger.info("Bevar Ukraine News bot started and webhooks set.")

async def on_shutdown(dp):
    logger.info("Stopping the news bot...")
    await bot.delete_webhook()
    session = await bot.get_session()
    await session.close()

if __name__ == "__main__":
    from aiogram import executor

    executor.start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=int(WEBAPP_PORT),
    )
