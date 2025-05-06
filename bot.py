from aiogram import Bot, Dispatcher
from handlers import router
from config import Config


async def main():
    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
