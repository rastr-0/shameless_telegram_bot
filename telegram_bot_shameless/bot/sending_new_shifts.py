from bot.handlers import database_shifts
from bot import custom_logger
import asyncio

from bot import custom_logger

# create logger
logger = custom_logger.setup_logging()

async def get_subscribed_users() -> list:
    # connection to database
    conn = await database_shifts.connect_to_database()
    # get subscribed users from database
    subscribed_users = await database_shifts.fetch_sql(conn, database_shifts.get_all_users_ids_sql)

    return subscribed_users

async def get_chat_ids_from_user_ids(bot, user_ids) -> list:
    chats_info = []
    for user_id in user_ids:
        chats_info.append(await bot.get_chat(int(user_id[0])))

    return chats_info

async def send_new_shifts(bot, interval) -> None:
    while True:
        # get user_ids and convert them to chat_ids
        chats_info = await get_chat_ids_from_user_ids(bot, await get_subscribed_users())
        # connection to database
        conn = await database_shifts.connect_to_database()
        recent_shifts = await database_shifts.fetch_sql(conn, database_shifts.get_recent_shifts_sql)

        full_message = ''

        for chat_info in chats_info:
            if recent_shifts:
                await bot.send_message(chat_info['id'], f"Привет\U0001F44B, {chat_info['first_name']}, на сайте появились новые смены либо обновились существующие!")
                
                for shift in recent_shifts:
                    text_shift = f"""
\U0001F4ACНазвание: {shift[0]}
\U0001F5D3Когда: {shift[1]}
\U0001F55BВо сколько: {shift[2]}
\U0001F4CDГде: {shift[3]}
\U0001F464Позиция: {shift[4]}
\U0001F4CAЗаполненность: {shift[5]}
-------------------------------------------------------
"""
                    if len(full_message + text_shift) < 4096:
                        full_message += text_shift
                    else:
                        await bot.send_message(chat_info['id'], full_message)
                        full_message = text_shift
                
                # logs
                logger.info('got new shifts', extra={'user_name' : chat_info['username'], 'user_id': chat_info['id']})

                if full_message:
                    await bot.send_message(chat_info['id'], full_message)
                
                # reset full_message for each user's answer
                full_message = ''

        # clean table
        await database_shifts.execute_sql(conn, database_shifts.clean_recent_shifts)
        
        await asyncio.sleep(interval)
