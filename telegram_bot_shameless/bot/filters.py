from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

# this class implements filter for determined non-state messages
# basically which bot recognizes and has responses
# but does not have specific state for them
class SpecificNonCommand(BoundFilter):
    async def check(self, message: types.Message):
        specific_messages = ['/start', '/Start', '/help', '/Help', '/menu',
        '/Menu', '/unsubscribe', '/Unsubscribe',
        '\u2022<u>Присылать тебе новые смены, сразу после их появления</u>',
        '\u2022<u>Показывать все доступные смены на сайте</u>',
        '\u2022<u>Сортировать и показывать конкретные смены на сайте</u>']

        return message.text in specific_messages
