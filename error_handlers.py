import io
import logging
import traceback

from aiogram.types import Update, ParseMode, ReplyKeyboardRemove
from aiogram.utils import exceptions

from settings import dp, bot, MY_ID


@dp.errors_handler(exception=exceptions.MessageTextIsEmpty)
async def empty_message_answer(update: Update, exception: Exception):
    current_state = dp.current_state(chat=update.message.chat.id)
    if current_state is None:
        return

    await current_state.finish()
    await update.message.answer('По запросу ничего не нашлось', reply_markup=ReplyKeyboardRemove())
    return True


@dp.errors_handler(exception=Exception)
async def base_exception_answer(update: Update, exception: Exception):
    with io.StringIO() as sio:
        traceback.print_exception(
            type(exception), exception, exception.__traceback__, None, sio
        )
        text = sio.getvalue()
        text = f'`{text}`'

    current_state = dp.current_state(chat=update.message.chat.id)
    if current_state is None:
        return

    await current_state.finish()
    await bot.send_message(chat_id=int(MY_ID), text=text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=ReplyKeyboardRemove())
    logging.exception(exception)
    return True
