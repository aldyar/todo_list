import asyncio
from aiogram import Bot, Dispatcher, types
from config import BOT_TOKEN
from app.database.models import async_main

from app.handlers import router

async def main():   
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_routers(router)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)

async def on_startup(dispatcher):
    await async_main()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


