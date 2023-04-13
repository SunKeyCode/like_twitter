from typing import Literal

from db_models.user_model import User
from sqlalchemy import Executable
from sqlalchemy.orm import selectinload


def user_include_relations(
    include_relations: Literal["all", "followers", "following"] | None,
    statement: Executable,
) -> Executable:
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
