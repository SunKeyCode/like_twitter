import logging
from typing import Union

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from db_models.follower_model import Follower
from db_models.user_model import User
from schemas.user_schema import CreateUserModel


async def create_user(session: AsyncSession, user_data: CreateUserModel) -> User:
    user = User(**user_data.dict())
    async with session.begin():
        session.add(user)

    return user


async def read_user(
        session: AsyncSession,
        user_id: int,
        include_relations: str = None,
) -> User:
    statement = select(User).where(User.user_id == user_id)
    if include_relations == "followers":
        statement = statement.options(
            selectinload(User.followers),
        )
    elif include_relations == "following":
        statement = statement.options(
            selectinload(User.following),
        )
    elif include_relations == "all":
        statement = statement.options(
            selectinload(User.followers),
            selectinload(User.following),
        )
    async with session.begin():
        user = await session.scalars(statement)
    return user.one_or_none()


async def read_all(
        session: AsyncSession,
        include_relations: str = None,
) -> list[User]:
    statement = select(User)

    if include_relations == "followers":
        statement = statement.options(
            selectinload(User.followers),
        )
    elif include_relations == "following":
        statement = statement.options(
            selectinload(User.following),
        )
    elif include_relations == "all":
        statement = statement.options(
            selectinload(User.followers),
            selectinload(User.following),
        )

    async with session.begin():
        user = await session.scalars(statement)
    return user.all()


async def follow_user(
        session: AsyncSession,
        user_who_follow: Union[User, int],
        user_id: int
) -> None:
    if isinstance(user_who_follow, User):
        who_fallow_id = user_who_follow.user_id
    elif isinstance(user_who_follow, int):
        who_fallow_id = user_who_follow
    else:
        raise TypeError

    async with session.begin():
        follower_association = Follower()
        follower_association.follower_id = who_fallow_id
        follower_association.user_id = user_id
        session.add(follower_association)


async def unfollow(
        session: AsyncSession,
        user_who_unfollow: Union[User, int],
        user_id: int
) -> None:
    if isinstance(user_who_unfollow, User):
        who_unfollow_id = user_who_unfollow.user_id
    elif isinstance(user_who_unfollow, int):
        who_unfollow_id = user_who_unfollow
    else:
        raise TypeError

    async with session.begin():
        await session.execute(
            delete(Follower)
            .where(Follower.follower_id == who_unfollow_id)
            .where(Follower.user_id == user_id)
        )
