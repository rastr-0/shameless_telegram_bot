# modules of aiogram
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
# files
from bot.handlers import database_shifts
from bot.handlers import states
from bot import custom_logger
# other moduless
import re
import asyncio

# create logger
logger = custom_logger.setup_logging()

def register_handlers(dp: Dispatcher) -> None:
    register_user_handlers(dp)


# function with provided keyboard markup
def keyboard(buttons_list):
    # settings for buttons
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons_list,
        resize_keyboard=True,
        input_field_placeholder='Выберите действие для бота'
    )

    return keyboard

"""
This part of code stands for command functions
"""

async def start_command(message: types.Message) -> None:
    """Bot introduces himself to user and asks for specific action with button
    """
    # answer for /start command
    text = """
<b>Привет</b>\U0001F44B!
Я бот\U0001F916, созданный помочь тебе отслеживать смены на сайте shameless.cz.
Что я могу?\U0001F914:
\u2022<u>Присылать тебе новые смены, сразу после их появления</u>
\u2022<u>Показывать все доступные смены на сайте</u>
\u2022<u>Сортировать и показывать конкретные смены на сайте</u>

Для просмотра всех доступных команд используй /help или /Help
"""
    # keyboard start-command buttons
    kb = [
        [types.KeyboardButton(text='\U0001F480Доступные смены на данный момент')],
        [types.KeyboardButton(text='\U0001F480Присылай мне новые смены (регулярно)')],
        [types.KeyboardButton(text='\U0001F480Покажи мне конкретные смены')]
    ]

    # logs
    logger.info('started bot', extra={'user_name' : message.from_user.username, 'user_id': message.from_user.id})

    await message.answer(text, reply_markup=keyboard(kb))


async def help_command(message: types.Message) -> None:
    text = """
Тебе доступны следующие команды (Все команды так же работают и с большой буквы):
\U000026AB/help - показывает все доступные команды
\U000026AB/start - запускает бота
\U000026AB/menu - открывает меню бота
\U000026AB/unsubscribe - отписывает тебя от рассылки смен
\U000026AB/report - показывает контакты, куда можно отправить информацию о баге или новой фиче бота
"""

    # keyboard menu buttons
    kb = [
        [types.KeyboardButton(text='/menu')],
        [types.KeyboardButton(text='/help')]
    ]

    await message.answer(text, reply_markup=keyboard(kb))


async def menu_command(message: types.Message) -> None:
    text = """
Ты можешь выбрать следующие действия для бота\U0001F9BE
\u2022<u>Присылать тебе новые смены, сразу после их появления или обновления</u>
\u2022<u>Показывать все доступные смены на сайте</u>
\u2022<u>Сортировать и показывать конкретные смены на сайте</u>
\u2022<u>/help</u> - список всех доступных команд
    """
    # keyboard menu-command buttons
    kb = [
        [types.KeyboardButton(text='\U0001F480Доступные смены на данный момент')],
        [types.KeyboardButton(text='\U0001F480Присылай мне новые смены (регулярно)')],
        [types.KeyboardButton(text='\U0001F480Покажи мне конкретные смены')],
        [types.KeyboardButton(text='/help')]
    ]

    await message.answer(text, reply_markup=keyboard(kb))


async def report_command(message: types.Message) -> None:
    text = """
\u2757Если ты заметил какой-то баг или у тебя есть идея для новых возможностей бота.
Обязательно напишите мне с пометкой shameless_bot.
telegram: @rastr_1
e-mail: romanmilko123@gmail.com
"""
    
    # keyboard menu buttons
    kb_menu = [
        [types.KeyboardButton(text='/menu')],
        [types.KeyboardButton(text='/help')]
    ]

    await message.answer(text, reply_markup=keyboard(kb_menu))

"""
This part of code stands for non-command functions
"""

async def show_available_shifts(message: types.Message) -> None:
    # connection to database
    conn = await database_shifts.connect_to_database()
    # count shifts
    amount_shifts = await database_shifts.fetch_sql(conn, database_shifts.count_shifts_sql)
    await message.answer(f'Было найдено {list(amount_shifts[0])[0]} смен')
    # get all available shifts
    available_shifts = await database_shifts.fetch_sql(conn, database_shifts.select_shifts_sql)
    full_message = ''
    # keyboard menu buttons
    kb = [
        [types.KeyboardButton(text='/menu')],
        [types.KeyboardButton(text='/help')]
    ]

    for shift in available_shifts:
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
            await message.answer(full_message, reply_markup=keyboard(kb))
            full_message = text_shift
    if full_message:
        await message.answer(full_message, reply_markup=keyboard(kb))

    # logs
    logger.info('showed all shifts 1', extra={'user_name' : message.from_user.username, 'user_id': message.from_user.id})


# set specific conditions for showing shifts
async def show_specific_shifts(message: types.Message, state: FSMContext) -> None:
    # connection to database
    conn = await database_shifts.connect_to_database()
    # answer for "choosing specific shifts"
    text = """
<b>Конечно</b>!
Ты можешь <u>отсортировать</u> смены по:
\U0001F5D3дате
\U0001F464позиции
\U0001F4CAколичеству людей на смене (маленькие / большие)

Начнем с \U0001F5D3даты
Введи дату либо промежуток. Формат: yyyy-mm-dd
К примеру, 2023-07-23 или 2023-08-01
\u26A0Для промежутка добавь дефис между датами (2023-07-23-2023-08-01)

Если тебе подходят все даты - напиши "любые / Любые"
"""
    await message.answer(text, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(states.SpecificShift.waiting_date.state)


async def handle_date(message: types.Message, state: FSMContext) -> None:
    all_dates = ['любые', 'Любые']
    date_matter = True
    if message.text in all_dates:
        date_matter = False

        text_all_dates = """
<b>Без проблем</b>\U0001F44D!
Давай теперь определимся с позицией\u270A
Ты можешь выбрать следущие позиции:
\U0001F480Crewboss
\U0001F480Pracovník
\U0001F480Záložník
\U0001F480Любая
"""
        # keyboard for position answer
        kb = [
            [types.KeyboardButton(text='\U0001F480Crewboss')],
            [types.KeyboardButton(text='\U0001F480Pracovník')],
            [types.KeyboardButton(text='\U0001F480Záložník')],
            [types.KeyboardButton(text='\U0001F480Любая')]
        ]

        await message.answer(text_all_dates, reply_markup=keyboard(kb))
        await state.update_data(choosen_date=message.text)
        await state.set_state(states.SpecificShift.waiting_position.state)

    one_date_re = r'\d{4}-\d{2}-\d{2}'
    match_first = re.match(one_date_re, message.text)

    interval_date_re = r'\d{4}-\d{2}-\d{2}-\d{4}-\d{2}-\d{2}'
    match_second = re.match(interval_date_re, message.text)
    if match_first or match_second:
        # keyboard confirm position buttons
        kb_confirm = [
            [types.KeyboardButton(text='\u2714Да')],
            [types.KeyboardButton(text='\u2716Нет')]
        ]

        text_right_date = f"""
<b>Супер</b>\U0001F44D!
Ты ввел дату <u>{message.text}</u>
Оставляем (Да / Нет)?
"""
        await message.answer(text_right_date, reply_markup=keyboard(kb_confirm))
        # create new variable with user's data
        await state.update_data(choosen_date=message.text)
        await state.set_state(states.SpecificShift.confirming_date.state)
    elif date_matter:
        text_wrong_date = """
Введи дату либо промежуток. Формат: yyyy-mm-dd
К примеру, 2023-07-23 или 2023-08-01
\u26A0Для промежутка добавь дефис между датами (2023-07-23-2023-08-01)
Если тебе подходят все даты - напиши "любые / Любые"
"""
        await message.answer(text_wrong_date)


async def confirm_date(message: types.Message, state: FSMContext) -> None:
    if message.text == '\u2716Нет':
        text_new_date = """
<b>Хорошо</b>\U0001F44D!
Введи дату либо промежуток снова. Формат: yyyy-mm-dd
К примеру, 2023-07-23 или 2023-08-01
\u26A0Для промежутка добавь дефис между датами (2023-07-23-2023-08-01)
Если тебе подходят все даты - напиши "любые / Любые"
"""
        await message.answer(text_new_date)
        await state.set_state(states.SpecificShift.waiting_date)
    elif message.text == '\u2714Да':
        # text for choosing position
        text_position = """
<b>Отлично</b>\U0001F44D!
Давай теперь определимся с позицией\u270A
Ты можешь выбрать следущие позиции:
\U0001F480Crewboss
\U0001F480Pracovník
\U0001F480Záložník
\U0001F480Любая
"""
        # keyboard for position answer
        kb = [
            [types.KeyboardButton(text='\U0001F480Crewboss')],
            [types.KeyboardButton(text='\U0001F480Pracovník')],
            [types.KeyboardButton(text='\U0001F480Záložník')],
            [types.KeyboardButton(text='\U0001F480Любая')]
        ]
        await message.answer(text_position, reply_markup=keyboard(kb))
        await state.set_state(states.SpecificShift.waiting_position)
    else:
        await message.answer('Выбери, пожалуйста, одно из действий на кнопках (\u2714Да / \u2716Нет)')


async def handle_position(message: types.Message, state: FSMContext) -> None:
    positions_list = ['\U0001F480Crewboss', '\U0001F480Pracovník',
                        '\U0001F480Záložník', '\U0001F480Любая']
    # wrong position
    if message.text not in positions_list:
        # keyboard for position answer
        kb = [
            [types.KeyboardButton(text='\U0001F480Crewboss')],
            [types.KeyboardButton(text='\U0001F480Pracovník')],
            [types.KeyboardButton(text='\U0001F480Záložník')],
            [types.KeyboardButton(text='\U0001F480Любая')]
        ]
        await message.answer('Выбери, пожалуйста, \U0001F480<u>позицию</u> из представленных на кнопках',
                                reply_markup=keyboard(kb))

        await state.set_state(states.SpecificShift.waiting_position)
    # right position
    else:
        # create new variable with user's data
        await state.update_data(choosen_position=message.text)
        # keyboard confirm position buttons
        kb = [
            [types.KeyboardButton(text='\u2714Да')],
            [types.KeyboardButton(text='\u2716Нет')]
        ]
        text_right_position = f"""
<b>Супер</b>\U0001F44D!
Ты выбрал эту позицию: <u>{message.text}</u>
Оставляем (Да / Нет)?
"""
        await message.answer(text_right_position, reply_markup=keyboard(kb))
        await state.set_state(states.SpecificShift.confirming_position.state)


async def confirm_position(message: types.Message, state: FSMContext) -> None:
    if message.text == '\u2716Нет':
        # keyboard confirm position buttons
        kb_position = [
            [types.KeyboardButton(text='\U0001F480Crewboss')],
            [types.KeyboardButton(text='\U0001F480Pracovník')],
            [types.KeyboardButton(text='\U0001F480Záložník')],
            [types.KeyboardButton(text='\U0001F480Любая')]
        ]
        text_new_position = """
Выбери одну из \U0001F480<u>позиций</u> заново
Ты можешь выбрать следущие позиции:
\U0001F480Crewboss
\U0001F480Pracovník
\U0001F480Záložník
\U0001F480Любая
"""
        await message.answer(text_new_position, reply_markup=keyboard(kb_position))
        await state.set_state(states.SpecificShift.waiting_position.state)
    elif message.text == '\u2714Да':
        # keyboard size of shifts buttons
        kb_shift_size = [
            [types.KeyboardButton(text='\U0001F535Маленькие')],
            [types.KeyboardButton(text='\U0001F534Большие')],
            [types.KeyboardButton(text='\U0001F7E0Любые')]
        ]
        text_shift_size = """
<b>Почти готово</b>\U0001F44D!
Осталось только выбрать размер смен
Какие смены тебе интересны?
\U0001F535Маленькие
\U0001F534Большие
\U0001F7E0Любые
"""
        await message.answer(text_shift_size, reply_markup=keyboard(kb_shift_size))
        await state.set_state(states.SpecificShift.waiting_shift_size.state)
    else:
        await message.answer('Выбери, пожалуйста, одно из действий на кнопках (\u2714Да / \u2716Нет)')


async def handle_shift_size(message: types.Message, state: FSMContext) -> None:
    shift_size_list = ['\U0001F535Маленькие', '\U0001F534Большие', '\U0001F7E0Любые']
    if message.text in shift_size_list:
        # keyboard confirming shift size buttons
        kb = [
            [types.KeyboardButton(text='\u2714Да')],
            [types.KeyboardButton(text='\u2716Нет')]
        ]
        text_right_shift_size = f"""
<b>Супер</b>\U0001F44D!
Ты выбрал <u>{message.text.lower()}</u> смены
Оставляем (Да / Нет)?
"""
        await message.answer(text_right_shift_size, reply_markup=keyboard(kb))
        # create new variable with user's data
        await state.update_data(choosen_shift_size=message.text)
        await state.set_state(states.SpecificShift.confirming_shift_size.state)
    else:
        # keyboard shift size buttons
        kb_shift_size = [
            [types.KeyboardButton(text='\U0001F535Маленькие')],
            [types.KeyboardButton(text='\U0001F534Большие')],
            [types.KeyboardButton(text='\U0001F7E0Любые')]
        ]
        await message.answer('Выбери, пожалуйста, <u>размер смены</u> из представленных на кнопках',
                                reply_markup=keyboard(shift_size))

        await state.set_state(states.SpecificShift.waiting_shift_size.state)


async def confirm_shift_size(message: types.Message, state: FSMContext) -> None:
    if message.text == '\u2716Нет':
        # keyboard confirm shift size buttons
        kb = [
            [types.KeyboardButton(text='\U0001F535Маленькие')],
            [types.KeyboardButton(text='\U0001F534Большие')],
            [types.KeyboardButton(text='\U0001F7E0Любые')]
        ]
        text_new_position = """
Выбери <u>размер смены</u> заново
Ты можешь выбрать следущие позиции:
\U0001F535Маленькие <= 10
\U0001F534Большие > 11
\U0001F7E0Любые
"""
        await message.answer(text_new_position, reply_markup=keyboard(kb))
        await state.set_state(states.SpecificShift.waiting_shift_size.state)
    elif message.text == '\u2714Да':
        text_final = """
\U0001F3C1<b>Все сделано</b>\U0001F44D!
Сейчас я пришлю тебе смены подходящие под твои требования
"""
        # keyboard menu buttons
        kb_menu = [
            [types.KeyboardButton(text='/menu')],
            [types.KeyboardButton(text='/help')]
        ]
        await message.answer(text_final, reply_markup=keyboard(kb_menu))

        # show shifts based on selected conditions
        data = await state.get_data()
        date = data.get('choosen_date')
        # start from 1 position to drop emoji
        position = data.get('choosen_position')[1:]
        shift_size = data.get('choosen_shift_size')[1:]
        conditions_variables = [date, position, shift_size]
        # connection to database
        conn = await database_shifts.connect_to_database()
        shifts_by_conditions = await database_shifts.get_shifts_by_conditions(conn, conditions_variables)

        # str for completing final message
        full_message = ''
        # count objects in tuple
        amount_shifts = len(shifts_by_conditions)
        await message.answer(f'Было найдено {amount_shifts} смен')

        # keyboard menu buttons
        kb_menu = [
            [types.KeyboardButton(text='/menu')],
            [types.KeyboardButton(text='/help')]
        ]
        # send shifts
        for shift in shifts_by_conditions:
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
                await message.answer(full_message, reply_markup=keyboard(kb_menu))
                full_message = text_shift
        if full_message:
            await message.answer(full_message, reply_markup=keyboard(kb_menu))

        # finish state
        await state.finish()

        # logs
        logger.info('showed specific shifts', extra={'user_name' : message.from_user.username, 'user_id': message.from_user.id})
    else:
        await message.answer('Выбери, пожалуйста, одно из действий на кнопках (\u2714Да / \u2716Нет)')


# add users ids to table for sending them new shifts
async def receive_new_shifts(message: types.Message) -> None:
    # get user id
    user_id = str(message.from_user.id)
    # connect to db
    conn = await database_shifts.connect_to_database()
    # check if user is already subscribed for receiving new shifts
    is_subscribed = await database_shifts.fetch_sql(conn, database_shifts.is_user_subscribed_sql, (user_id,))
    if not is_subscribed:
        # logs
        logger.info('subscribed for getting shifts', extra={'user_name' : message.from_user.username, 'user_id': message.from_user.id})
        await message.answer("""
Теперь ты будешь регулярно получать новые смены\U0001F642
В случае, если ты больше не хочешь получать новые смены - используй команду
/unsubscribe или /Unsubscribe
    """)
        await database_shifts.execute_sql(conn, database_shifts.add_user_id_sql, (user_id,))
        #asyncio.create_task(check_new_shifts())
    else:
        # keyboard menu buttons
        kb_menu = [
            [types.KeyboardButton(text='/menu')],
            [types.KeyboardButton(text='/help')]
        ]
        await message.answer("""
Ты уже подписан на рассылку смен\U0001FAE1
В случае, если ты больше не хочешь получать новые смены - используй команду
/unsubscribe или /Unsubscribe
        """, reply_markup=keyboard(kb_menu))


async def unsubscribe_getting_shifts(message: types.Message) -> None:
    # get user id
    user_id = str(message.from_user.id)
    # connection to database
    conn = await database_shifts.connect_to_database()
    # check if user is in database before trying to delete
    is_subscribed = await database_shifts.fetch_sql(conn, database_shifts.is_user_subscribed_sql, (user_id,))
    if is_subscribed:
        # delete user id from database
        await database_shifts.execute_sql(conn, database_shifts.delete_user_id_sql, (user_id,))
        # logs
        logger.info('unsubscribed from getting shifts', extra={'user_name' : message.from_user.username, 'user_id': message.from_user.id})

        await message.answer('Ты отписался от рассылок смен\U0001F44D. Но всегда сможешь подписаться заново!')
    else:
        await message.answer('Ты не подписан на рассылку смен, поэтому и отписаться не можешь\U0001F601')


# function with registered functions
def register_user_handlers(dp: Dispatcher):
    # register functions-answers to messages
    dp.register_message_handler(start_command, commands=['start', 'Start'])
    dp.register_message_handler(menu_command, commands=['menu', 'Menu'])
    dp.register_message_handler(help_command, commands=['help', 'Help'])
    dp.register_message_handler(show_available_shifts, Text('\U0001F480Доступные смены на данный момент'))
    dp.register_message_handler(show_specific_shifts, Text('\U0001F480Покажи мне конкретные смены'))
    dp.register_message_handler(handle_date, state=states.SpecificShift.waiting_date)
    dp.register_message_handler(confirm_date, state=states.SpecificShift.confirming_date)
    dp.register_message_handler(handle_position, state=states.SpecificShift.waiting_position)
    dp.register_message_handler(confirm_position, state=states.SpecificShift.confirming_position)
    dp.register_message_handler(handle_shift_size, state=states.SpecificShift.waiting_shift_size)
    dp.register_message_handler(confirm_shift_size, state=states.SpecificShift.confirming_shift_size)
    dp.register_message_handler(receive_new_shifts, Text('\U0001F480Присылай мне новые смены (регулярно)'))
    dp.register_message_handler(unsubscribe_getting_shifts, commands=['unsubscribe', 'Unsubscribe'])
    dp.register_message_handler(report_command, commands=['report', 'Report'])
