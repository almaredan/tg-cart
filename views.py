import logging

from aiogram import types
from aiogram.dispatcher import filters, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode, ReplyKeyboardMarkup

from settings import dp
import models
import messages
import states
import services


@dp.message_handler(commands=['error'])
async def wtf(message: types.Message):
    raise Exception('Пошел нахуй!')


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.answer(messages.GREETING)


@dp.message_handler(commands=['get_dishes'])
async def get_dishes(message: types.Message):
    for dish in models.Dish.select():
        await message.answer(f"{dish}. Подробнее: /dish{dish.id}\nДобавить в список: /plan{dish.id}",
                             parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['plan'])
async def plan1(message: types.Message):
    await states.Plan.week_choosing.set()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Current', 'Next')
    markup.add('Cancel')

    await message.answer('Выбери неделю', reply_markup=markup)


@dp.message_handler(state=states.Plan.week_choosing)
async def plan2(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardRemove()
    dishes_list = services.get_plan(message.text == 'Next')
    await message.answer('\n'.join([str(d) for d in dishes_list]), reply_markup=markup)
    await state.finish()


@dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=['^/dish([0-9]*)']))
async def item(message: types.Message, regexp_command):
    dish = models.Dish[regexp_command.group(1)]

    await message.answer(f"<b>{dish.link}</b>", parse_mode=ParseMode.HTML)
    recipe = ['\nСостав:']
    for r in dish.recipe:
        recipe.append(str(r))
    await message.answer('\n'.join(recipe))


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.answer(f'Отменил {current_state}', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['add_dish'])
async def add_dish(message: types.Message):
    await states.DishAdditions.start.set()
    await message.answer('Дай мне ссылку на блюдо с сайта eda.ru\nОтменить:\t/cancel')


@dp.message_handler(lambda message: str.startswith(message.text, 'https://eda.ru/'), state=states.DishAdditions.start)
async def process_dish(message: types.Message, state: FSMContext):
    await state.finish()
    dish = services.add_recipe(message.text)
    await message.answer(f"{dish}. Подробнее: /dish{dish.id}")


@dp.message_handler(commands=['plan_dish'])
async def plan_dish1(message: types.Message):
    await states.DishPlanner.dish_choosing.set()
    await message.answer('Выбери блюдо, которое хочешь добавить в список')
    for dish in models.Dish.select():
        await message.answer(f"{dish}. Добавить: /dish{dish.id}", parse_mode=ParseMode.MARKDOWN)
    await message.answer('Отменить:\t/cancel')


@dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=['^/plan([0-9]*)']))
@dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=['^/dish([0-9]*)']),
                    state=states.DishPlanner.dish_choosing)
async def plan_dish2(message: types.Message, regexp_command, state: FSMContext):
    dish = models.Dish[regexp_command.group(1)]

    await state.update_data(dish=dish)
    await states.DishPlanner.week_choosing.set()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Current', 'Next')
    markup.add('Cancel')

    await message.answer('Выбери неделю', reply_markup=markup)


@dp.message_handler(lambda message: message.text not in ['Current', 'Next'], state=states.Plan.week_choosing)
@dp.message_handler(lambda message: message.text not in ['Current', 'Next'], state=states.DishPlanner.week_choosing)
async def plan_dish3_bad(message: types.Message):
    return await message.reply("Я не понимаю, про какую неделю ты говоришь")


@dp.message_handler(state=states.DishPlanner.week_choosing)
async def plan_dish3(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['week'] = message.text

        next_week = data['week'] == 'Next'
        services.add_dish_to_list(data['dish'], next_week)

        markup = types.ReplyKeyboardRemove()
        await message.answer('Добавил', reply_markup=markup)

    # Finish conversation
    await state.finish()
