from peewee_moves import DatabaseManager

from models import database

manager = DatabaseManager(database)
print(manager.revision())
manager.create('models')
manager.upgrade()
