import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

DATABASE = 'tg-cart.sqlite'
API_TOKEN = os.getenv('API_TOKEN')
MY_ID = os.getenv('MY_ID')

# Configure logging
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
