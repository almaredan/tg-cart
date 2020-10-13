from aiogram.dispatcher.filters.state import State, StatesGroup


class DishAdditions(StatesGroup):
    start = State()


class DishPlanner(StatesGroup):
    dish_choosing = State()
    week_choosing = State()


class Plan(StatesGroup):
    week_choosing = State()

