from typing import Literal

from sqlalchemy import Select
from sqlalchemy.orm import selectinload

from db_models.user_model import User


def user_include_relations(
    include_relations: Literal["all", "followers", "following"] | None,
    statement: Select,
) -> Select:
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

    return statement
