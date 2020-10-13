from typing import List

import peewee as pw

import models
import utils


def add_recipe(link: str):
    parsed_recipe = utils.parse_recipe(link)
    with models.database.transaction():
        dish = models.Dish.get_or_create(link=link, name=parsed_recipe.name)[0]
        dish.image_link = parsed_recipe.image
        dish.save()

        for prod in parsed_recipe.ingredients:
            product = models.Product.get_or_create(name=prod.name, measure=prod.measure)[0]
            product.save()

            recipe = models.Recipe.get_or_create(dish=dish, ingredient=product)[0]
            recipe.quantity = prod.quantity
            recipe.save()

        dish.is_parsed = True
        dish.save()
    return dish


def delete_dish(dish: models.Dish):
    with models.database.transaction():
        delete_recipe = models.Recipe.delete().where(models.Recipe.dish == dish)
        delete_recipe.execute()

        clear_list = models.DishesList.delete().where(models.DishesList.dish == dish)
        clear_list.execute()

        dish.delete_instance()


def delete_product(product: models.Product):
    if product.recipe.exists():
        return
    with models.database.transaction():
        product.delete_instance()


def add_product(name: str, measure: str = 'шт'):
    with models.database.transaction():
        product = models.Product.get_or_create(name=name, measure=measure)[0]
        product.save()


def add_dish_to_list(dish: models.Dish, next_week=True):
    if next_week:
        week = utils.get_next_week_number()
        year = utils.get_next_week_year()
    else:
        week = utils.get_curr_week_number()
        year = utils.get_curr_week_year()
    with models.database.transaction():
        list_position = models.DishesList.get_or_create(dish=dish, week=week, year=year)[0]
        list_position.save()


def remove_outdated_dishes():
    with models.database.transaction():
        week = utils.get_curr_week_number()
        year = utils.get_curr_week_year()
        deleting = models.DishesList.delete().where(
            (models.DishesList.week < week) & (models.DishesList.year <= year)
        )
        deleting.execute()


def add_product_to_cart(product: models.Product, quantity: int):
    with models.database.transaction():
        cart_position = models.Cart.get_or_create(product=product)[0]
        cart_position.quantity += quantity
        cart_position.save()


def add_dish_to_cart(dish: models.Dish):
    with models.database.transaction():
        products = dish.recipe
        for r in products:
            add_product_to_cart(r.ingredient, r.quantity)


def remove_product_from_cart(product: models.Product, quantity=None):
    try:
        cart_position = models.Cart.get(product=product)
        if quantity is not None:
            cart_position.quantity -= quantity
            cart_position.save()
        if cart_position.quantity < 0 or quantity is None:
            cart_position.delete_instance()
    except pw.DoesNotExist:
        pass


def remove_dish_from_cart(dish: models.Dish):
    for r in dish.recipe:
        remove_product_from_cart(r.product, r.quantity)


def get_plan(next_week: bool) -> List[models.DishesList]:
    if next_week:
        week = utils.get_next_week_number()
        year = utils.get_next_week_year()
    else:
        week = utils.get_curr_week_number()
        year = utils.get_curr_week_year()
    return models.DishesList.select().where(
        (models.DishesList.week == week) & (models.DishesList.year == year)
    )
