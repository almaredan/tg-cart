import peewee as pw
from peewee import DoesNotExist

import settings
import utils

database = pw.SqliteDatabase(settings.DATABASE)


class BaseModel(pw.Model):
    class Meta:
        database = database


class Dish(BaseModel):
    id = pw.AutoField(primary_key=True)
    link = pw.CharField(unique=True)
    name = pw.CharField()
    image_link = pw.CharField(null=True)
    is_parsed = pw.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'dishes'
        constraints = [pw.Check('link like "https://eda.ru/%"')]


class Product(BaseModel):
    id = pw.AutoField(primary_key=True)
    name = pw.CharField()
    measure = pw.CharField(default='шт')

    def __str__(self):
        return f'{self.name} [{self.measure}]'

    class Meta:
        db_table = 'products'
        indexes = (
            (('name', 'measure'), True),
        )


class Recipe(BaseModel):
    dish = pw.ForeignKeyField(Dish, backref='recipe')
    ingredient = pw.ForeignKeyField(Product, backref='recipe')
    quantity = pw.DecimalField(default=1)

    def __str__(self):
        return f'{self.ingredient.name} {self.quantity} {self.ingredient.measure}'

    class Meta:
        db_table = 'recipes'


class User(BaseModel):
    id = pw.IntegerField(primary_key=True)
    nickname = pw.CharField(unique=True)

    class Meta:
        db_table = 'users'


class DishesList(BaseModel):
    id = pw.AutoField(primary_key=True)
    dish = pw.ForeignKeyField(Dish)
    week = pw.IntegerField(default=utils.get_next_week_number())
    year = pw.IntegerField(default=utils.get_next_week_year())

    def __str__(self):
        return str(self.dish)

    class Meta:
        db_table = 'dishes_list'
        indexes = (
            (('dish', 'week', 'year'), True),
        )


class Cart(BaseModel):
    id = pw.AutoField(primary_key=True)
    product = pw.ForeignKeyField(Product, unique=True)
    quantity = pw.DecimalField(default=0)

    def __str__(self):
        return f'{self.product.name} {self.quantity} {self.product.measure}'

    class Meta:
        db_table = 'cart'
