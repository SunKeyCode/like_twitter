import factory
import factory.fuzzy as fuzzy
import random

from database import async_session
from models import User, Tweet, Like, Media


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = async_session()

    user_name: str = factory.Faker('user_name')
    first_name: str = factory.Faker('first_name')
    last_name: str = factory.Faker('last_name')
    # reg_date
