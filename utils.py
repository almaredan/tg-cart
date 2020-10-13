import datetime
from typing import NamedTuple, List
import re
import json

import requests
from bs4 import BeautifulSoup


def get_next_week_number():
    return (datetime.datetime.now() + datetime.timedelta(weeks=1)).isocalendar()[1]


def get_next_week_year():
    return (datetime.datetime.now() + datetime.timedelta(weeks=1)).isocalendar()[0]


def get_curr_week_number():
    return datetime.datetime.now().isocalendar()[1]


def get_curr_week_year():
    return datetime.datetime.now().isocalendar()[0]


class Ingredient(NamedTuple):
    name: str
    quantity: int
    measure: str


class ParsedRecipe(NamedTuple):
    name: str
    image: str
    ingredients: List[Ingredient]


def parse_recipe(url: str) -> ParsedRecipe:
    response = requests.get(url)
    content = response.content.decode()
    soup = BeautifulSoup(content, features="html.parser")
    name = soup.find('h1', {'class': 'recipe__name g-h1'}).text
    name = re.sub("^\s+|\n|\r|\s+$", '', name)
    image = soup.find('div', {'class': 'photo-list-preview'}).find('img').get('src')
    ingredients = list()
    section_ = soup.find('div', {'class': 'ingredients-list layout__content-col'})
    ingr_list = section_.find_all('p', {'class': 'ingredients-list__content-item content-item js-cart-ingredients'})
    for ingr in ingr_list:
        di = json.loads(ingr.get('data-ingredient-object'))
        amount = di['amount'].split(' ')
        measure, quantity = _extract_quantity_and_measure(amount)
        ingredients.append(
            Ingredient(name=di['name'], quantity=quantity, measure=measure)
        )

    return ParsedRecipe(name=name, image=image, ingredients=ingredients)


def _extract_quantity_and_measure(amount):
    try:
        quantity = int(amount[0])
        measure = ' '.join(amount[1:])
    except ValueError:
        quantity = 1
        measure = ' '.join(amount)
    if str.startswith(measure, '½'):
        quantity = 0.5
        measure = ' '.join(measure.split(' ')[1:])
    if str.startswith(measure, '¼'):
        quantity = 0.25
        measure = ' '.join(measure.split(' ')[1:])
    if str.startswith(measure, '¾'):
        quantity = 0.75
        measure = ' '.join(measure.split(' ')[1:])
    if str.startswith(measure, '⅓'):
        quantity = 0.333
        measure = ' '.join(measure.split(' ')[1:])
    if str.startswith(measure, '⅔'):
        quantity = 0.666
        measure = ' '.join(measure.split(' ')[1:])
    if str.startswith(measure, '⅕'):
        quantity = 0.2
        measure = ' '.join(measure.split(' ')[1:])
    if str.startswith(measure, '⅖'):
        quantity = 0.4
        measure = ' '.join(measure.split(' ')[1:])
    if str.startswith(measure, '⅗'):
        quantity = 0.6
        measure = ' '.join(measure.split(' ')[1:])
    if str.startswith(measure, '⅘'):
        quantity = 0.8
        measure = ' '.join(measure.split(' ')[1:])
    if str.startswith(measure, 'шт'):
        measure = 'шт'
    if str.startswith(measure, 'гр'):
        measure = 'г'
    if str.startswith(measure, 'килог'):
        measure = 'кг'
    if str.startswith(measure, 'лит'):
        measure = 'л'
    if str.startswith(measure, 'миллил'):
        measure = 'мл'
    if str.startswith(measure, 'стол'):
        measure = 'мл'
        quantity *= 15
    return measure, quantity
