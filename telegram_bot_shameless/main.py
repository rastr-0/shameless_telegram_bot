from bot.handlers.user_handlers import register_user_handlers
from bot.sending_new_shifts import send_new_shifts

import sys
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.builtin import Command
from aiogram.dispatcher import filters
from dotenv import load_dotenv
import os
import asyncio


async def main():
    # bot connection
    load_dotenv('.env')
    token = os.getenv('TOKEN_API')
    storage = MemoryStorage()
    bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot, storage=storage)

    register_user_handlers(dp)

    try:
        polling_task = asyncio.create_task(dp.start_polling())
        # 24/7 runned task for gettings new shifts by subs
        interval_seconds = 10
        send_new_shifts_task = asyncio.create_task(send_new_shifts(bot, interval_seconds))
        
        await asyncio.gather(polling_task, send_new_shifts_task)

    except Exception as _ex:
        print(_ex)
    finally:
        await bot.close()
        await dp.storage.close()
        await dp.storage.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
