import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from handlers import routers_list
async def main():
    load_dotenv()

    bot = Bot(token=os.getenv('BOT_TOKEN'))
    dp = Dispatcher()

    dp.include_routers(*routers_list)

    await dp.start_polling(bot)


import asyncio

asyncio.run(main())
