import factory
from faker import Faker
import factory.fuzzy as fuzzy
import random

from models import User
from database import async_session


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = async_session()

    username = factory.Faker('username')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
