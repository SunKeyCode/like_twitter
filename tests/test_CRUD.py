import pytest

from sqlalchemy.exc import IntegrityError

import _crud
from fake_factory import UserFactory
from _schemas import CreateUserModel
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


async def test_create_user(db_session):
    fake_user = CreateUserModel(user_name="user_form _test")
    user = await crud.create_user(db_session, fake_user)
    assert user.user_id is not None
    # fake_user = CreateUserModel(user_name="user_form _test")
    with pytest.raises(IntegrityError):
        await crud.create_user(db_session, fake_user)


async def test_create_user_with_same_username(db_session):
    fake_user = CreateUserModel(user_name="user_form _test")
    with pytest.raises(IntegrityError):
        await crud.create_user(db_session, fake_user)
