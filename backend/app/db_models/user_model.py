from datetime import datetime
from typing import List

from sqlalchemy import Date, Identity, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base_class import Base
from db_models.follower_model import Follower


class User(Base):
    __tablename__ = "table_users"

    user_id = mapped_column(Integer, Identity(always=True), primary_key=True)
    user_name = mapped_column(String(20), nullable=False, unique=True)
    password = mapped_column(String, nullable=False)
    first_name = mapped_column(String(50), nullable=True)
    last_name = mapped_column(String(50), nullable=True)
    reg_date = mapped_column(Date, default=datetime.today)

    followers: Mapped[List["User"]] = relationship(
        "User",
        secondary="table_followers",
        primaryjoin=user_id == Follower.user_id,
        secondaryjoin=user_id == Follower.follower_id,
        viewonly=True,
        lazy="raise",
    )

    following: Mapped[List["User"]] = relationship(
        secondary="table_followers",
        primaryjoin=user_id == Follower.follower_id,
        secondaryjoin=user_id == Follower.user_id,
        viewonly=True,
        lazy="raise",
    )

    def __repr__(self) -> str:
        return f"User(id={self.user_id}, user_name={self.user_name})"
