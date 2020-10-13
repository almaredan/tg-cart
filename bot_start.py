from aiogram import executor

from settings import dp
import views
import error_handlers


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
